"""
Real-time Training Progress Monitoring
Lightweight script to monitor training progress from history file
"""
import json
import matplotlib.pyplot as plt
import time
import os
from pathlib import Path


def plot_live_training(history_path='checkpoints/training_history.json', refresh_interval=5):
    """
    Monitor training progress in real-time
    Args:
        history_path: Path to training history JSON
        refresh_interval: Seconds between refreshes
    """
    plt.ion()  # Interactive mode
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Real-Time Training Progress', fontsize=16, fontweight='bold')
    
    print("="*60)
    print("REAL-TIME TRAINING MONITOR")
    print("="*60)
    print(f"Monitoring: {history_path}")
    print(f"Refresh interval: {refresh_interval}s")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    try:
        while True:
            if not os.path.exists(history_path):
                print(f"\rWaiting for training history file... ", end='', flush=True)
                time.sleep(refresh_interval)
                continue
            
            # Load history
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            epochs = list(range(len(history['train']['g_loss'])))
            
            if not epochs:
                print(f"\rNo data yet... ", end='', flush=True)
                time.sleep(refresh_interval)
                continue
            
            # Clear previous plots
            for ax in axes.flat:
                ax.clear()
            
            # Generator Loss
            axes[0, 0].plot(epochs, history['train']['g_loss'], 'b-', linewidth=2)
            axes[0, 0].set_title('Generator Loss', fontweight='bold')
            axes[0, 0].set_xlabel('Epoch')
            axes[0, 0].set_ylabel('Loss')
            axes[0, 0].grid(True, alpha=0.3)
            
            # Discriminator Loss
            axes[0, 1].plot(epochs, history['train']['d_loss'], 'r-', linewidth=2)
            axes[0, 1].set_title('Discriminator Loss', fontweight='bold')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Loss')
            axes[0, 1].grid(True, alpha=0.3)
            
            # L1 Loss
            axes[0, 2].plot(epochs, history['train']['l1_loss'], 'g-', linewidth=2)
            axes[0, 2].set_title('L1 Loss (Pixel-wise)', fontweight='bold')
            axes[0, 2].set_xlabel('Epoch')
            axes[0, 2].set_ylabel('Loss')
            axes[0, 2].grid(True, alpha=0.3)
            
            # Perceptual Loss
            axes[1, 0].plot(epochs, history['train']['perceptual_loss'], 'purple', linewidth=2)
            axes[1, 0].set_title('Perceptual Loss', fontweight='bold')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Loss')
            axes[1, 0].grid(True, alpha=0.3)
            
            # PSNR
            axes[1, 1].plot(epochs, history['val']['psnr'], 'orange', linewidth=2, marker='o')
            axes[1, 1].set_title('Validation PSNR', fontweight='bold')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('PSNR (dB)')
            axes[1, 1].grid(True, alpha=0.3)
            
            # Add best PSNR marker
            best_psnr_idx = history['val']['psnr'].index(max(history['val']['psnr']))
            best_psnr = max(history['val']['psnr'])
            axes[1, 1].axhline(y=best_psnr, color='r', linestyle='--', alpha=0.5, 
                              label=f'Best: {best_psnr:.2f} dB')
            axes[1, 1].legend()
            
            # SSIM
            axes[1, 2].plot(epochs, history['val']['ssim'], 'brown', linewidth=2, marker='s')
            axes[1, 2].set_title('Validation SSIM', fontweight='bold')
            axes[1, 2].set_xlabel('Epoch')
            axes[1, 2].set_ylabel('SSIM')
            axes[1, 2].grid(True, alpha=0.3)
            
            # Add best SSIM marker
            best_ssim = max(history['val']['ssim'])
            axes[1, 2].axhline(y=best_ssim, color='r', linestyle='--', alpha=0.5,
                              label=f'Best: {best_ssim:.4f}')
            axes[1, 2].legend()
            
            plt.tight_layout()
            plt.pause(0.1)
            
            # Print current status
            current_epoch = epochs[-1]
            current_psnr = history['val']['psnr'][-1]
            current_ssim = history['val']['ssim'][-1]
            
            print(f"\rEpoch {current_epoch}: PSNR={current_psnr:.4f} dB, SSIM={current_ssim:.4f} | Best PSNR={best_psnr:.4f} dB @ epoch {best_psnr_idx}", 
                  end='', flush=True)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        plt.ioff()
        plt.show()
    except Exception as e:
        print(f"\n\nError: {e}")
        plt.ioff()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor training progress in real-time')
    parser.add_argument('--history_path', type=str, default='checkpoints/training_history.json',
                        help='Path to training history JSON file')
    parser.add_argument('--refresh', type=int, default=5,
                        help='Refresh interval in seconds')
    
    args = parser.parse_args()
    
    plot_live_training(args.history_path, args.refresh)
