"""
Utility functions for training and evaluation
"""
import torch
import numpy as np
import os
from torchvision.utils import save_image
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import json

def denormalize(tensor):
    """Convert normalized tensor [-1, 1] to [0, 1]"""
    return (tensor + 1.0) / 2.0

def calculate_psnr(img1, img2):
    """
    Calculate PSNR between two images
    Args:
        img1, img2: torch tensors of shape (B, C, H, W) in range [-1, 1]
    Returns:
        Average PSNR across batch
    """
    # Denormalize to [0, 1]
    img1 = denormalize(img1).cpu().numpy()
    img2 = denormalize(img2).cpu().numpy()
    
    psnr_values = []
    for i in range(img1.shape[0]):
        # Transpose to (H, W, C) for skimage
        im1 = np.transpose(img1[i], (1, 2, 0))
        im2 = np.transpose(img2[i], (1, 2, 0))
        psnr_values.append(psnr(im1, im2, data_range=1.0))
    
    return np.mean(psnr_values)

def calculate_ssim(img1, img2):
    """
    Calculate SSIM between two images
    Args:
        img1, img2: torch tensors of shape (B, C, H, W) in range [-1, 1]
    Returns:
        Average SSIM across batch
    """
    # Denormalize to [0, 1]
    img1 = denormalize(img1).cpu().numpy()
    img2 = denormalize(img2).cpu().numpy()
    
    ssim_values = []
    for i in range(img1.shape[0]):
        # Transpose to (H, W, C) for skimage
        im1 = np.transpose(img1[i], (1, 2, 0))
        im2 = np.transpose(img2[i], (1, 2, 0))
        ssim_values.append(ssim(im1, im2, multichannel=True, channel_axis=2, data_range=1.0))
    
    return np.mean(ssim_values)

def save_checkpoint(state, filename):
    """Save model checkpoint"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    torch.save(state, filename)
    print(f"Checkpoint saved to {filename}")

def load_checkpoint(checkpoint_path, generator, discriminator, optimizer_G, optimizer_D):
    """Load model checkpoint"""
    if os.path.isfile(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path)
        
        generator.load_state_dict(checkpoint['generator_state_dict'])
        discriminator.load_state_dict(checkpoint['discriminator_state_dict'])
        optimizer_G.load_state_dict(checkpoint['optimizer_G_state_dict'])
        optimizer_D.load_state_dict(checkpoint['optimizer_D_state_dict'])
        
        epoch = checkpoint['epoch']
        best_psnr = checkpoint.get('best_psnr', 0.0)
        
        print(f"Loaded checkpoint from epoch {epoch}")
        return epoch, best_psnr
    else:
        print(f"No checkpoint found at {checkpoint_path}")
        return 0, 0.0

def save_sample_images(blur_imgs, real_imgs, fake_imgs, epoch, sample_dir):
    """Save sample images for visual comparison"""
    os.makedirs(sample_dir, exist_ok=True)
    
    # Denormalize images
    blur_imgs = denormalize(blur_imgs)
    real_imgs = denormalize(real_imgs)
    fake_imgs = denormalize(fake_imgs)
    
    # Save first 4 images from batch
    n_samples = min(4, blur_imgs.size(0))
    
    # Create comparison grid
    comparison = torch.cat([
        blur_imgs[:n_samples],
        fake_imgs[:n_samples],
        real_imgs[:n_samples]
    ], dim=0)
    
    save_path = os.path.join(sample_dir, f"epoch_{epoch:03d}.png")
    save_image(comparison, save_path, nrow=n_samples, padding=2)
    print(f"Sample images saved to {save_path}")

def plot_training_history(history, save_path):
    """Plot training history"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Loss plots
    axes[0, 0].plot(history['train']['g_loss'], label='Generator Loss')
    axes[0, 0].set_title('Generator Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    axes[0, 1].plot(history['train']['d_loss'], label='Discriminator Loss', color='orange')
    axes[0, 1].set_title('Discriminator Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    axes[0, 2].plot(history['train']['l1_loss'], label='L1 Loss', color='green')
    axes[0, 2].set_title('L1 Loss')
    axes[0, 2].set_xlabel('Epoch')
    axes[0, 2].set_ylabel('Loss')
    axes[0, 2].legend()
    axes[0, 2].grid(True)
    
    axes[1, 0].plot(history['train']['perceptual_loss'], label='Perceptual Loss', color='red')
    axes[1, 0].set_title('Perceptual Loss')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Loss')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    axes[1, 1].plot(history['val']['psnr'], label='PSNR', color='purple')
    axes[1, 1].set_title('Validation PSNR')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('PSNR (dB)')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    axes[1, 2].plot(history['val']['ssim'], label='SSIM', color='brown')
    axes[1, 2].set_title('Validation SSIM')
    axes[1, 2].set_xlabel('Epoch')
    axes[1, 2].set_ylabel('SSIM')
    axes[1, 2].legend()
    axes[1, 2].grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Training history plot saved to {save_path}")

def save_training_history(history, save_path):
    """Save training history to JSON"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Convert numpy types to Python native types
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    history_serializable = convert_types(history)
    
    with open(save_path, 'w') as f:
        json.dump(history_serializable, f, indent=4)
    print(f"Training history saved to {save_path}")

class AverageMeter:
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
    
    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
