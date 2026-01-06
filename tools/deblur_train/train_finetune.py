"""
Fine-Tuning Script for >32 dB PSNR Target
Includes: SSIM loss, Discriminator freezing, Cosine annealing with warm restarts
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import os
import time
import argparse
from tqdm import tqdm
import random
import numpy as np

from config_finetune import Config
from models import GeneratorResNet, Discriminator, FeatureExtractor
from dataset import create_train_val_datasets
from utils import (
    calculate_psnr, calculate_ssim, save_checkpoint, load_checkpoint,
    save_sample_images, AverageMeter, plot_training_history, save_training_history
)


def set_seed(seed):
    """Set random seed for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


class SSIMLoss(nn.Module):
    """SSIM Loss for structural similarity optimization"""
    def __init__(self):
        super(SSIMLoss, self).__init__()
    
    def forward(self, pred, target):
        """Calculate 1 - SSIM as loss"""
        # Simple SSIM calculation (for efficiency)
        # Normalize to [0, 1] from [-1, 1]
        pred = (pred + 1) / 2
        target = (target + 1) / 2
        
        # Constants for SSIM
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        
        # Calculate means
        mu_pred = torch.mean(pred, dim=[2, 3], keepdim=True)
        mu_target = torch.mean(target, dim=[2, 3], keepdim=True)
        
        # Calculate variances and covariance
        sigma_pred = torch.var(pred, dim=[2, 3], keepdim=True, unbiased=False)
        sigma_target = torch.var(target, dim=[2, 3], keepdim=True, unbiased=False)
        sigma_pred_target = torch.mean((pred - mu_pred) * (target - mu_target), dim=[2, 3], keepdim=True)
        
        # SSIM formula
        numerator = (2 * mu_pred * mu_target + C1) * (2 * sigma_pred_target + C2)
        denominator = (mu_pred ** 2 + mu_target ** 2 + C1) * (sigma_pred + sigma_target + C2)
        
        ssim = numerator / (denominator + 1e-8)
        
        # Return 1 - SSIM as loss (we want to minimize)
        return 1 - torch.mean(ssim)


def train_one_epoch(generator, discriminator, feature_extractor, train_loader, 
                     optimizer_G, optimizer_D, criterion_GAN, criterion_pixelwise, 
                     criterion_perceptual, criterion_ssim, config, epoch, writer, 
                     scaler=None, freeze_discriminator=False):
    """Train for one epoch with SSIM loss"""
    generator.train()
    
    if freeze_discriminator:
        discriminator.eval()  # Freeze discriminator
        for param in discriminator.parameters():
            param.requires_grad = False
    else:
        discriminator.train()
        for param in discriminator.parameters():
            param.requires_grad = True
    
    # Meters for tracking
    g_loss_meter = AverageMeter()
    d_loss_meter = AverageMeter()
    l1_loss_meter = AverageMeter()
    perceptual_loss_meter = AverageMeter()
    adv_loss_meter = AverageMeter()
    ssim_loss_meter = AverageMeter()
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{config.NUM_EPOCHS} {'[D FROZEN]' if freeze_discriminator else ''}")
    
    for batch_idx, (blur_imgs, sharp_imgs) in enumerate(pbar):
        batch_size = blur_imgs.size(0)
        blur_imgs = blur_imgs.to(config.DEVICE)
        sharp_imgs = sharp_imgs.to(config.DEVICE)
        
        # Adversarial ground truths
        valid = torch.ones((batch_size, 1, 16, 16), device=config.DEVICE, requires_grad=False)
        fake = torch.zeros((batch_size, 1, 16, 16), device=config.DEVICE, requires_grad=False)
        
        # ==================== Train Generator ====================
        optimizer_G.zero_grad()
        
        if config.USE_AMP and scaler is not None:
            with torch.cuda.amp.autocast():
                # Generate deblurred images
                fake_sharp = generator(blur_imgs)
                
                # Pixel-wise loss
                loss_pixel = criterion_pixelwise(fake_sharp, sharp_imgs)
                
                # Perceptual loss
                real_features = feature_extractor(sharp_imgs)
                fake_features = feature_extractor(fake_sharp)
                loss_perceptual = criterion_perceptual(fake_features, real_features)
                
                # SSIM loss
                loss_ssim = criterion_ssim(fake_sharp, sharp_imgs) if config.USE_SSIM_LOSS else 0.0
                
                # Adversarial loss
                if not freeze_discriminator:
                    pred_fake = discriminator(blur_imgs, fake_sharp)
                    loss_GAN = criterion_GAN(pred_fake, valid)
                else:
                    loss_GAN = torch.tensor(0.0, device=config.DEVICE)
                
                # Total generator loss
                loss_G = (config.LAMBDA_PIXEL * loss_pixel + 
                         config.LAMBDA_PERCEPTUAL * loss_perceptual + 
                         config.LAMBDA_ADV * loss_GAN)
                
                if config.USE_SSIM_LOSS:
                    loss_G += config.LAMBDA_SSIM * loss_ssim
            
            scaler.scale(loss_G).backward()
            scaler.unscale_(optimizer_G)
            torch.nn.utils.clip_grad_norm_(generator.parameters(), config.GRADIENT_CLIP)
            scaler.step(optimizer_G)
        else:
            # Generate deblurred images
            fake_sharp = generator(blur_imgs)
            
            # Pixel-wise loss
            loss_pixel = criterion_pixelwise(fake_sharp, sharp_imgs)
            
            # Perceptual loss
            real_features = feature_extractor(sharp_imgs)
            fake_features = feature_extractor(fake_sharp)
            loss_perceptual = criterion_perceptual(fake_features, real_features)
            
            # SSIM loss
            loss_ssim = criterion_ssim(fake_sharp, sharp_imgs) if config.USE_SSIM_LOSS else 0.0
            
            # Adversarial loss
            if not freeze_discriminator:
                pred_fake = discriminator(blur_imgs, fake_sharp)
                loss_GAN = criterion_GAN(pred_fake, valid)
            else:
                loss_GAN = torch.tensor(0.0, device=config.DEVICE)
            
            # Total generator loss
            loss_G = (config.LAMBDA_PIXEL * loss_pixel + 
                     config.LAMBDA_PERCEPTUAL * loss_perceptual + 
                     config.LAMBDA_ADV * loss_GAN)
            
            if config.USE_SSIM_LOSS:
                loss_G += config.LAMBDA_SSIM * loss_ssim
            
            loss_G.backward()
            torch.nn.utils.clip_grad_norm_(generator.parameters(), config.GRADIENT_CLIP)
            optimizer_G.step()
        
        # ==================== Train Discriminator ====================
        if not freeze_discriminator:
            optimizer_D.zero_grad()
            
            if config.USE_AMP and scaler is not None:
                with torch.cuda.amp.autocast():
                    # Real loss
                    pred_real = discriminator(blur_imgs, sharp_imgs)
                    loss_real = criterion_GAN(pred_real, valid)
                    
                    # Fake loss
                    pred_fake = discriminator(blur_imgs, fake_sharp.detach())
                    loss_fake = criterion_GAN(pred_fake, fake)
                    
                    # Total discriminator loss
                    loss_D = 0.5 * (loss_real + loss_fake)
                
                scaler.scale(loss_D).backward()
                scaler.unscale_(optimizer_D)
                torch.nn.utils.clip_grad_norm_(discriminator.parameters(), config.GRADIENT_CLIP)
                scaler.step(optimizer_D)
            else:
                # Real loss
                pred_real = discriminator(blur_imgs, sharp_imgs)
                loss_real = criterion_GAN(pred_real, valid)
                
                # Fake loss
                pred_fake = discriminator(blur_imgs, fake_sharp.detach())
                loss_fake = criterion_GAN(pred_fake, fake)
                
                # Total discriminator loss
                loss_D = 0.5 * (loss_real + loss_fake)
                
                loss_D.backward()
                torch.nn.utils.clip_grad_norm_(discriminator.parameters(), config.GRADIENT_CLIP)
                optimizer_D.step()
        else:
            loss_D = torch.tensor(0.0, device=config.DEVICE)
        
        # Update scaler after both generator and discriminator
        if config.USE_AMP and scaler is not None:
            scaler.update()
        
        # Update meters
        g_loss_meter.update(loss_G.item(), batch_size)
        d_loss_meter.update(loss_D.item() if not freeze_discriminator else 0.0, batch_size)
        l1_loss_meter.update(loss_pixel.item(), batch_size)
        perceptual_loss_meter.update(loss_perceptual.item(), batch_size)
        adv_loss_meter.update(loss_GAN.item() if not freeze_discriminator else 0.0, batch_size)
        if config.USE_SSIM_LOSS:
            ssim_loss_meter.update(loss_ssim.item(), batch_size)
        
        # Update progress bar
        pbar.set_postfix({
            'G': f'{g_loss_meter.avg:.4f}',
            'D': f'{d_loss_meter.avg:.4f}',
            'L1': f'{l1_loss_meter.avg:.4f}',
            'SSIM_L': f'{ssim_loss_meter.avg:.4f}' if config.USE_SSIM_LOSS else 'N/A'
        })
        
        # Log to TensorBoard
        if batch_idx % config.PRINT_FREQ == 0:
            global_step = epoch * len(train_loader) + batch_idx
            writer.add_scalar('Train/Generator_Loss', g_loss_meter.avg, global_step)
            writer.add_scalar('Train/Discriminator_Loss', d_loss_meter.avg, global_step)
            writer.add_scalar('Train/L1_Loss', l1_loss_meter.avg, global_step)
            writer.add_scalar('Train/Perceptual_Loss', perceptual_loss_meter.avg, global_step)
            writer.add_scalar('Train/Adversarial_Loss', adv_loss_meter.avg, global_step)
            if config.USE_SSIM_LOSS:
                writer.add_scalar('Train/SSIM_Loss', ssim_loss_meter.avg, global_step)
    
    return {
        'g_loss': g_loss_meter.avg,
        'd_loss': d_loss_meter.avg,
        'l1_loss': l1_loss_meter.avg,
        'perceptual_loss': perceptual_loss_meter.avg,
        'adv_loss': adv_loss_meter.avg,
        'ssim_loss': ssim_loss_meter.avg if config.USE_SSIM_LOSS else 0.0
    }


@torch.no_grad()
def validate(generator, val_loader, config, epoch, writer):
    """Validate the model"""
    generator.eval()
    
    psnr_meter = AverageMeter()
    ssim_meter = AverageMeter()
    
    pbar = tqdm(val_loader, desc=f"Validation Epoch {epoch}")
    
    # Store sample images for visualization
    sample_blur = None
    sample_real = None
    sample_fake = None
    
    for batch_idx, (blur_imgs, sharp_imgs) in enumerate(pbar):
        blur_imgs = blur_imgs.to(config.DEVICE)
        sharp_imgs = sharp_imgs.to(config.DEVICE)
        
        # Generate deblurred images
        fake_sharp = generator(blur_imgs)
        
        # Calculate metrics
        psnr_value = calculate_psnr(fake_sharp, sharp_imgs)
        ssim_value = calculate_ssim(fake_sharp, sharp_imgs)
        
        psnr_meter.update(psnr_value, blur_imgs.size(0))
        ssim_meter.update(ssim_value, blur_imgs.size(0))
        
        # Save first batch for visualization
        if batch_idx == 0:
            sample_blur = blur_imgs[:4]
            sample_real = sharp_imgs[:4]
            sample_fake = fake_sharp[:4]
        
        pbar.set_postfix({
            'PSNR': f'{psnr_meter.avg:.2f}',
            'SSIM': f'{ssim_meter.avg:.4f}'
        })
    
    # Log to TensorBoard
    writer.add_scalar('Val/PSNR', psnr_meter.avg, epoch)
    writer.add_scalar('Val/SSIM', ssim_meter.avg, epoch)
    
    # Add sample images to TensorBoard
    if sample_blur is not None:
        from torchvision.utils import make_grid
        from utils import denormalize
        
        comparison = torch.cat([
            denormalize(sample_blur),
            denormalize(sample_fake),
            denormalize(sample_real)
        ], dim=0)
        grid = make_grid(comparison, nrow=4, padding=2)
        writer.add_image('Validation/Blur_Fake_Real', grid, epoch)
    
    return {
        'psnr': psnr_meter.avg,
        'ssim': ssim_meter.avg
    }


def main():
    parser = argparse.ArgumentParser(description='Fine-Tune Image Deblurring Model')
    parser.add_argument('--epochs', type=int, default=None, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=None, help='Batch size')
    args = parser.parse_args()
    
    config = Config()
    
    # Override config with command-line arguments
    if args.epochs is not None:
        config.NUM_EPOCHS = args.epochs
    if args.batch_size is not None:
        config.BATCH_SIZE = args.batch_size
    
    # Set random seed
    set_seed(config.SEED)
    
    # Create directories
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(config.SAMPLE_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    # Print configuration
    print("="*80)
    print("FINE-TUNING CONFIGURATION")
    print("="*80)
    print(f"Device: {config.DEVICE}")
    print(f"Resume from: {config.RESUME_PATH}")
    print(f"Batch Size: {config.BATCH_SIZE}")
    print(f"Epochs: {config.NUM_EPOCHS}")
    print(f"Learning Rate: {config.LEARNING_RATE_G}")
    print(f"Loss Weights - Pixel: {config.LAMBDA_PIXEL}, Perceptual: {config.LAMBDA_PERCEPTUAL}, SSIM: {config.LAMBDA_SSIM}")
    print(f"Target: PSNR >{config.TARGET_PSNR} dB, SSIM >{config.TARGET_SSIM}")
    print(f"Discriminator Freeze: First {config.FREEZE_DISCRIMINATOR_EPOCHS} epochs")
    print("="*80)
    
    # Create datasets
    print("\nLoading datasets...")
    train_dataset, val_dataset = create_train_val_datasets(
        root_dir=config.DATASET_ROOT,
        train_split=config.TRAIN_SPLIT,
        img_size=config.IMG_SIZE,
        augment_train=config.USE_ADVANCED_AUG
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        num_workers=config.NUM_WORKERS,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=config.NUM_WORKERS,
        pin_memory=True
    )
    
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    
    # Initialize models
    print("\nInitializing models...")
    generator = GeneratorResNet(
        in_channels=config.IN_CHANNELS,
        out_channels=config.OUT_CHANNELS,
        n_residual_blocks=config.N_RESIDUAL_BLOCKS
    ).to(config.DEVICE)
    
    discriminator = Discriminator(
        in_channels=config.IN_CHANNELS
    ).to(config.DEVICE)
    
    feature_extractor = FeatureExtractor().to(config.DEVICE)
    feature_extractor.eval()
    
    # Loss functions
    criterion_GAN = nn.MSELoss()
    criterion_pixelwise = nn.L1Loss()
    criterion_perceptual = nn.L1Loss()
    criterion_ssim = SSIMLoss()
    
    # Optimizers
    optimizer_G = torch.optim.Adam(
        generator.parameters(),
        lr=config.LEARNING_RATE_G,
        betas=(config.BETA1, config.BETA2)
    )
    
    optimizer_D = torch.optim.Adam(
        discriminator.parameters(),
        lr=config.LEARNING_RATE_D,
        betas=(config.BETA1, config.BETA2)
    )
    
    # Learning rate schedulers - Cosine annealing with warm restarts
    scheduler_G = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer_G, T_0=config.COSINE_T0, T_mult=config.COSINE_TMULT, 
        eta_min=config.MIN_LR
    )
    scheduler_D = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer_D, T_0=config.COSINE_T0, T_mult=config.COSINE_TMULT,
        eta_min=config.MIN_LR
    )
    
    # Mixed precision training
    scaler = torch.cuda.amp.GradScaler() if config.USE_AMP else None
    
    # Resume from checkpoint
    start_epoch = 0
    best_psnr = 0.0
    best_ssim = 0.0
    
    if config.RESUME and os.path.exists(config.RESUME_PATH):
        print(f"\nLoading checkpoint from {config.RESUME_PATH}...")
        start_epoch, best_psnr = load_checkpoint(
            config.RESUME_PATH, generator, discriminator, optimizer_G, optimizer_D
        )
        print(f"Resumed from epoch {start_epoch}, best PSNR: {best_psnr:.4f} dB")
        start_epoch += 1
    
    # TensorBoard writer
    writer = SummaryWriter(config.LOG_DIR)
    
    # Training history
    history = {
        'train': {
            'g_loss': [],
            'd_loss': [],
            'l1_loss': [],
            'perceptual_loss': [],
            'adv_loss': [],
            'ssim_loss': []
        },
        'val': {
            'psnr': [],
            'ssim': []
        }
    }
    
    # Early stopping
    early_stopping_counter = 0
    best_epoch = start_epoch
    
    # Training loop
    print("\n" + "="*80)
    print("STARTING FINE-TUNING")
    print("="*80)
    
    start_time = time.time()
    
    for epoch in range(start_epoch, start_epoch + config.NUM_EPOCHS):
        epoch_start_time = time.time()
        
        # Determine if discriminator should be frozen
        freeze_d = epoch < (start_epoch + config.FREEZE_DISCRIMINATOR_EPOCHS)
        
        # Train
        train_metrics = train_one_epoch(
            generator, discriminator, feature_extractor, train_loader,
            optimizer_G, optimizer_D, criterion_GAN, criterion_pixelwise,
            criterion_perceptual, criterion_ssim, config, epoch, writer, scaler,
            freeze_discriminator=freeze_d
        )
        
        # Validate
        val_metrics = validate(generator, val_loader, config, epoch, writer)
        
        # Update learning rate
        scheduler_G.step()
        scheduler_D.step()
        
        # Update history
        history['train']['g_loss'].append(train_metrics['g_loss'])
        history['train']['d_loss'].append(train_metrics['d_loss'])
        history['train']['l1_loss'].append(train_metrics['l1_loss'])
        history['train']['perceptual_loss'].append(train_metrics['perceptual_loss'])
        history['train']['adv_loss'].append(train_metrics['adv_loss'])
        history['train']['ssim_loss'].append(train_metrics['ssim_loss'])
        history['val']['psnr'].append(val_metrics['psnr'])
        history['val']['ssim'].append(val_metrics['ssim'])
        
        epoch_time = time.time() - epoch_start_time
        
        # Print epoch summary
        print(f"\n{'='*80}")
        print(f"EPOCH {epoch} COMPLETED ({epoch_time/60:.1f} min)")
        print(f"{'='*80}")
        print(f"Val PSNR: {val_metrics['psnr']:.4f} dB | Target: {config.TARGET_PSNR} dB")
        print(f"Val SSIM: {val_metrics['ssim']:.4f} | Target: {config.TARGET_SSIM}")
        print(f"LR (G/D): {optimizer_G.param_groups[0]['lr']:.2e} / {optimizer_D.param_groups[0]['lr']:.2e}")
        
        # Save checkpoint
        is_best = val_metrics['psnr'] > best_psnr + config.MIN_DELTA
        if is_best:
            best_psnr = val_metrics['psnr']
            best_ssim = val_metrics['ssim']
            best_epoch = epoch
            early_stopping_counter = 0
            print(f"🎉 NEW BEST! PSNR: {best_psnr:.4f} dB, SSIM: {best_ssim:.4f}")
        else:
            early_stopping_counter += 1
        
        if (epoch + 1) % config.SAVE_FREQ == 0 or is_best:
            checkpoint = {
                'epoch': epoch,
                'generator_state_dict': generator.state_dict(),
                'discriminator_state_dict': discriminator.state_dict(),
                'optimizer_G_state_dict': optimizer_G.state_dict(),
                'optimizer_D_state_dict': optimizer_D.state_dict(),
                'best_psnr': best_psnr,
                'train_metrics': train_metrics,
                'val_metrics': val_metrics
            }
            
            checkpoint_path = os.path.join(config.CHECKPOINT_DIR, f'finetune_epoch_{epoch:03d}.pth')
            save_checkpoint(checkpoint, checkpoint_path)
            
            if is_best:
                best_path = os.path.join(config.CHECKPOINT_DIR, 'best_model_finetune.pth')
                save_checkpoint(checkpoint, best_path)
                print(f"✅ Saved to: {best_path}")
        
        # Generate sample images
        if (epoch + 1) % config.SAMPLE_FREQ == 0:
            with torch.no_grad():
                blur_imgs, sharp_imgs = next(iter(val_loader))
                blur_imgs = blur_imgs.to(config.DEVICE)
                sharp_imgs = sharp_imgs.to(config.DEVICE)
                
                fake_sharp = generator(blur_imgs)
                save_sample_images(blur_imgs, sharp_imgs, fake_sharp, epoch, config.SAMPLE_DIR)
        
        # Save history after each epoch
        history_path = config.MONITOR_HISTORY
        save_training_history(history, history_path)
        
        # Check if target achieved (but keep training for maximum quality!)
        if val_metrics['psnr'] >= config.TARGET_PSNR and val_metrics['ssim'] >= config.TARGET_SSIM:
            print(f"\n{'='*80}")
            print("🎯 TARGET ACHIEVED! Continuing training for maximum quality...")
            print(f"{'='*80}")
            print(f"PSNR: {val_metrics['psnr']:.4f} dB (target: {config.TARGET_PSNR}) ✓")
            print(f"SSIM: {val_metrics['ssim']:.4f} (target: {config.TARGET_SSIM}) ✓")
            print(f"Will continue training to get the clearest possible images.")
            print(f"{'='*80}\n")
            # Don't break - keep training for best possible quality!
        
        # Early stopping check
        if early_stopping_counter >= config.EARLY_STOPPING_PATIENCE:
            print(f"\n{'='*80}")
            print(f"EARLY STOPPING")
            print(f"{'='*80}")
            print(f"No improvement for {config.EARLY_STOPPING_PATIENCE} epochs.")
            print(f"Best: PSNR {best_psnr:.4f} dB, SSIM {best_ssim:.4f} at epoch {best_epoch}")
            print(f"{'='*80}\n")
            break
        
        print("="*80 + "\n")
    
    # Training complete
    total_time = time.time() - start_time
    print(f"\n{'='*80}")
    print("FINE-TUNING COMPLETE!")
    print(f"{'='*80}")
    print(f"Total time: {total_time/3600:.2f} hours")
    print(f"Best PSNR: {best_psnr:.4f} dB")
    print(f"Best SSIM: {best_ssim:.4f}")
    print(f"Best model: {os.path.join(config.CHECKPOINT_DIR, 'best_model_finetune.pth')}")
    print(f"{'='*80}\n")
    
    # Plot training history
    plot_path = os.path.join(config.CHECKPOINT_DIR, 'training_history_finetune.png')
    plot_training_history(history, plot_path)
    
    writer.close()


if __name__ == '__main__':
    main()
