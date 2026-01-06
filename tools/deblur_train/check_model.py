"""
Check current model performance from checkpoint
"""
import torch
import os

def check_checkpoint(checkpoint_path):
    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint not found: {checkpoint_path}")
        return None
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    
    print("="*80)
    print(f"CHECKPOINT: {checkpoint_path}")
    print("="*80)
    
    epoch = checkpoint.get('epoch', 'N/A')
    best_psnr = checkpoint.get('best_psnr', 'N/A')
    
    print(f"Epoch: {epoch}")
    print(f"Best PSNR: {best_psnr:.4f} dB" if isinstance(best_psnr, (int, float)) else f"Best PSNR: {best_psnr}")
    
    if 'val_metrics' in checkpoint:
        val_metrics = checkpoint['val_metrics']
        psnr = val_metrics.get('psnr', 'N/A')
        ssim = val_metrics.get('ssim', 'N/A')
        
        print(f"\nValidation Metrics:")
        print(f"  PSNR: {psnr:.4f} dB" if isinstance(psnr, (int, float)) else f"  PSNR: {psnr}")
        print(f"  SSIM: {ssim:.4f}" if isinstance(ssim, (int, float)) else f"  SSIM: {ssim}")
        
        # Check if target is met
        if isinstance(psnr, (int, float)) and isinstance(ssim, (int, float)):
            print(f"\nTarget Status:")
            print(f"  PSNR >32 dB: {'✅ YES' if psnr > 32 else '❌ NO (need +' + f'{32-psnr:.2f} dB)'}")
            print(f"  SSIM >0.95: {'✅ YES' if ssim > 0.95 else '❌ NO (need +' + f'{0.95-ssim:.4f})'}")
    
    if 'train_metrics' in checkpoint:
        train_metrics = checkpoint['train_metrics']
        print(f"\nTraining Losses:")
        print(f"  Generator: {train_metrics.get('g_loss', 'N/A'):.6f}" if isinstance(train_metrics.get('g_loss'), (int, float)) else f"  Generator: N/A")
        print(f"  Discriminator: {train_metrics.get('d_loss', 'N/A'):.6f}" if isinstance(train_metrics.get('d_loss'), (int, float)) else f"  Discriminator: N/A")
    
    print("="*80)
    
    return checkpoint

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', default='checkpoints/best_model1.pth', help='Path to checkpoint')
    args = parser.parse_args()
    
    check_checkpoint(args.checkpoint)
