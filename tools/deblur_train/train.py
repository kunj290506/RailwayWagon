"""
Comprehensive Training Script for Image Deblurring
Contest-ready with detailed metrics tracking
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

from config import Config
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


def train_one_epoch(generator, discriminator, feature_extractor, train_loader, 
                     optimizer_G, optimizer_D, criterion_GAN, criterion_pixelwise, 
                     criterion_perceptual, config, epoch, writer, scaler=None):
    """Train for one epoch"""
    generator.train()
    discriminator.train()
    
    # Meters for tracking
    g_loss_meter = AverageMeter()
    d_loss_meter = AverageMeter()
    l1_loss_meter = AverageMeter()
    perceptual_loss_meter = AverageMeter()
    adv_loss_meter = AverageMeter()
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{config.NUM_EPOCHS}")
    
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
                
                # Adversarial loss
                pred_fake = discriminator(blur_imgs, fake_sharp)
                loss_GAN = criterion_GAN(pred_fake, valid)
                
                # Total generator loss
                loss_G = (config.LAMBDA_PIXEL * loss_pixel + 
                         config.LAMBDA_PERCEPTUAL * loss_perceptual + 
                         config.LAMBDA_ADV * loss_GAN)
            
            scaler.scale(loss_G).backward()
            # Gradient clipping for stability
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
            
            # Adversarial loss
            pred_fake = discriminator(blur_imgs, fake_sharp)
            loss_GAN = criterion_GAN(pred_fake, valid)
            
            # Total generator loss
            loss_G = (config.LAMBDA_PIXEL * loss_pixel + 
                     config.LAMBDA_PERCEPTUAL * loss_perceptual + 
                     config.LAMBDA_ADV * loss_GAN)
            
            loss_G.backward()
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(generator.parameters(), config.GRADIENT_CLIP)
            optimizer_G.step()
        
        # ==================== Train Discriminator ====================
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
            # Gradient clipping for stability
            scaler.unscale_(optimizer_D)
            torch.nn.utils.clip_grad_norm_(discriminator.parameters(), config.GRADIENT_CLIP)
            scaler.step(optimizer_D)
            scaler.update()
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
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(discriminator.parameters(), config.GRADIENT_CLIP)
            optimizer_D.step()
        
        # Update meters
        g_loss_meter.update(loss_G.item(), batch_size)
        d_loss_meter.update(loss_D.item(), batch_size)
        l1_loss_meter.update(loss_pixel.item(), batch_size)
        perceptual_loss_meter.update(loss_perceptual.item(), batch_size)
        adv_loss_meter.update(loss_GAN.item(), batch_size)
        
        # Update progress bar
        pbar.set_postfix({
            'G_loss': f'{g_loss_meter.avg:.4f}',
            'D_loss': f'{d_loss_meter.avg:.4f}',
            'L1': f'{l1_loss_meter.avg:.4f}'
        })
        
        # Log to TensorBoard
        if batch_idx % config.PRINT_FREQ == 0:
            global_step = epoch * len(train_loader) + batch_idx
            writer.add_scalar('Train/Generator_Loss', g_loss_meter.avg, global_step)
            writer.add_scalar('Train/Discriminator_Loss', d_loss_meter.avg, global_step)
            writer.add_scalar('Train/L1_Loss', l1_loss_meter.avg, global_step)
            writer.add_scalar('Train/Perceptual_Loss', perceptual_loss_meter.avg, global_step)
            writer.add_scalar('Train/Adversarial_Loss', adv_loss_meter.avg, global_step)
    
    return {
        'g_loss': g_loss_meter.avg,
        'd_loss': d_loss_meter.avg,
        'l1_loss': l1_loss_meter.avg,
        'perceptual_loss': perceptual_loss_meter.avg,
        'adv_loss': adv_loss_meter.avg
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
    parser = argparse.ArgumentParser(description='Train Image Deblurring Model')
    parser.add_argument('--epochs', type=int, default=None, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=None, help='Batch size')
    parser.add_argument('--resume', type=str, default=None, help='Path to checkpoint to resume from')
    args = parser.parse_args()
    
    config = Config()
    
    # Override config with command-line arguments
    if args.epochs is not None:
        config.NUM_EPOCHS = args.epochs
    if args.batch_size is not None:
        config.BATCH_SIZE = args.batch_size
    if args.resume is not None:
        config.RESUME = True
        config.RESUME_PATH = args.resume
    
    # Set random seed
    set_seed(config.SEED)
    
    # Create directories
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(config.SAMPLE_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    # Print configuration
    print("="*80)
    print("TRAINING CONFIGURATION")
    print("="*80)
    print(f"Device: {config.DEVICE}")
    print(f"Dataset: {config.DATASET_ROOT}")
    print(f"Batch Size: {config.BATCH_SIZE}")
    print(f"Epochs: {config.NUM_EPOCHS}")
    print(f"Image Size: {config.IMG_SIZE}")
    print(f"Learning Rate (G/D): {config.LEARNING_RATE_G} / {config.LEARNING_RATE_D}")
    print(f"Loss Weights - Pixel: {config.LAMBDA_PIXEL}, Perceptual: {config.LAMBDA_PERCEPTUAL}, Adv: {config.LAMBDA_ADV}")
    print(f"Mixed Precision Training: {config.USE_AMP}")
    print("="*80)
    
    # Create datasets
    print("\nLoading datasets...")
    train_dataset, val_dataset = create_train_val_datasets(
        root_dir=config.DATASET_ROOT,
        train_split=config.TRAIN_SPLIT,
        img_size=config.IMG_SIZE,
        augment_train=True
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
    
    # Count parameters
    g_params = sum(p.numel() for p in generator.parameters() if p.requires_grad)
    d_params = sum(p.numel() for p in discriminator.parameters() if p.requires_grad)
    print(f"Generator parameters: {g_params:,}")
    print(f"Discriminator parameters: {d_params:,}")
    
    # Loss functions
    criterion_GAN = nn.MSELoss()
    criterion_pixelwise = nn.L1Loss()
    criterion_perceptual = nn.L1Loss()
    
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
    
    # Learning rate schedulers
    scheduler_G = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_G, mode='max', factor=0.5, patience=10, verbose=True
    )
    scheduler_D = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer_D, mode='max', factor=0.5, patience=10, verbose=True
    )
    
    # Mixed precision training
    scaler = torch.cuda.amp.GradScaler() if config.USE_AMP else None
    
    # Resume from checkpoint if specified
    start_epoch = 0
    best_psnr = 0.0
    
    if config.RESUME and os.path.exists(config.RESUME_PATH):
        start_epoch, best_psnr = load_checkpoint(
            config.RESUME_PATH, generator, discriminator, optimizer_G, optimizer_D
        )
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
            'adv_loss': []
        },
        'val': {
            'psnr': [],
            'ssim': []
        }
    }
    
    # Early stopping
    early_stopping_counter = 0
    best_epoch = 0
    
    # Training loop
    print("\n" + "="*80)
    print("STARTING TRAINING")
    print("="*80)
    print(f"Early Stopping: Enabled (patience={config.EARLY_STOPPING_PATIENCE})")
    print(f"Gradient Clipping: {config.GRADIENT_CLIP}")
    print("="*80)
    
    start_time = time.time()
    
    for epoch in range(start_epoch, config.NUM_EPOCHS):
        epoch_start_time = time.time()
        
        # Train
        train_metrics = train_one_epoch(
            generator, discriminator, feature_extractor, train_loader,
            optimizer_G, optimizer_D, criterion_GAN, criterion_pixelwise,
            criterion_perceptual, config, epoch, writer, scaler
        )
        
        # Validate
        val_metrics = validate(generator, val_loader, config, epoch, writer)
        
        # Update learning rate
        scheduler_G.step(val_metrics['psnr'])
        scheduler_D.step(val_metrics['psnr'])
        
        # Update history
        history['train']['g_loss'].append(train_metrics['g_loss'])
        history['train']['d_loss'].append(train_metrics['d_loss'])
        history['train']['l1_loss'].append(train_metrics['l1_loss'])
        history['train']['perceptual_loss'].append(train_metrics['perceptual_loss'])
        history['train']['adv_loss'].append(train_metrics['adv_loss'])
        history['val']['psnr'].append(val_metrics['psnr'])
        history['val']['ssim'].append(val_metrics['ssim'])
        
        epoch_time = time.time() - epoch_start_time
        total_time = time.time() - start_time
        
        # Calculate time estimates
        avg_epoch_time = total_time / (epoch + 1)
        remaining_epochs = config.NUM_EPOCHS - epoch - 1
        estimated_remaining = avg_epoch_time * remaining_epochs
        estimated_remaining_hours = estimated_remaining / 3600
        
        # Print detailed epoch summary
        print(f"\n{'='*80}")
        print(f"EPOCH {epoch}/{config.NUM_EPOCHS-1} COMPLETED")
        print(f"{'='*80}")
        print(f"\nTIME INFORMATION:")
        print(f"  This epoch:        {epoch_time:.1f} seconds ({epoch_time/60:.1f} minutes)")
        print(f"  Total elapsed:     {total_time/3600:.2f} hours")
        print(f"  Average per epoch: {avg_epoch_time/60:.1f} minutes")
        print(f"  Estimated remain:  {estimated_remaining_hours:.1f} hours")
        print(f"  Progress:          {epoch+1}/{config.NUM_EPOCHS} ({(epoch+1)/config.NUM_EPOCHS*100:.1f}%)")
        
        print(f"\nTRAINING LOSSES:")
        print(f"  Generator Loss:    {train_metrics['g_loss']:.6f}")
        print(f"  Discriminator Loss: {train_metrics['d_loss']:.6f}")
        print(f"  L1 Loss:           {train_metrics['l1_loss']:.6f}")
        print(f"  Perceptual Loss:   {train_metrics['perceptual_loss']:.6f}")
        print(f"  Adversarial Loss:  {train_metrics['adv_loss']:.6f}")
        
        print(f"\nVALIDATION METRICS:")
        print(f"  PSNR:  {val_metrics['psnr']:.4f} dB")
        print(f"  SSIM:  {val_metrics['ssim']:.6f}")
        
        print(f"\nLEARNING RATES:")
        print(f"  Generator:     {optimizer_G.param_groups[0]['lr']:.6f}")
        print(f"  Discriminator: {optimizer_D.param_groups[0]['lr']:.6f}")
        print(f"{'='*80}\n")
        
        # Save checkpoint
        is_best = val_metrics['psnr'] > best_psnr + config.MIN_DELTA
        if is_best:
            best_psnr = val_metrics['psnr']
            best_epoch = epoch
            early_stopping_counter = 0
            print(f"🎉 New best PSNR: {best_psnr:.4f} dB (Improvement: {val_metrics['psnr'] - (best_psnr - val_metrics['psnr'] + config.MIN_DELTA):.4f} dB)")
        else:
            early_stopping_counter += 1
            print(f"No improvement for {early_stopping_counter} epoch(s). Best: {best_psnr:.4f} dB at epoch {best_epoch}")
        
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
            
            checkpoint_path = os.path.join(config.CHECKPOINT_DIR, f'checkpoint_epoch_{epoch:03d}.pth')
            save_checkpoint(checkpoint, checkpoint_path)
            
            if is_best:
                best_path = os.path.join(config.CHECKPOINT_DIR, 'best_model.pth')
                save_checkpoint(checkpoint, best_path)
        
        # Generate sample images
        if (epoch + 1) % config.SAMPLE_FREQ == 0:
            with torch.no_grad():
                # Get a batch from validation set
                blur_imgs, sharp_imgs = next(iter(val_loader))
                blur_imgs = blur_imgs.to(config.DEVICE)
                sharp_imgs = sharp_imgs.to(config.DEVICE)
                
                fake_sharp = generator(blur_imgs)
                save_sample_images(blur_imgs, sharp_imgs, fake_sharp, epoch, config.SAMPLE_DIR)
        
        # Early stopping check
        if early_stopping_counter >= config.EARLY_STOPPING_PATIENCE:
            print(f"\n{'='*80}")
            print(f"EARLY STOPPING TRIGGERED")
            print(f"{'='*80}")
            print(f"No improvement for {config.EARLY_STOPPING_PATIENCE} consecutive epochs.")
            print(f"Best PSNR: {best_psnr:.4f} dB at epoch {best_epoch}")
            print(f"Stopping training early.")
            print(f"{'='*80}\n")
            break
    
    # Training complete
    total_time = time.time() - start_time
    print(f"\n{'='*80}")
    print("TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"Total training time: {total_time/3600:.2f} hours")
    print(f"Best validation PSNR: {best_psnr:.4f} dB")
    print(f"Best model saved to: {os.path.join(config.CHECKPOINT_DIR, 'best_model.pth')}")
    print(f"{'='*80}\n")
    
    # Save training history
    history_path = os.path.join(config.CHECKPOINT_DIR, 'training_history.json')
    save_training_history(history, history_path)
    
    # Plot training history
    plot_path = os.path.join(config.CHECKPOINT_DIR, 'training_history.png')
    plot_training_history(history, plot_path)
    
    writer.close()


if __name__ == '__main__':
    main()
