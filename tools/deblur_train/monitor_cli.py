"""
Command-Line Training Monitor (No GUI)
Simple text-based monitoring for training progress
"""
import json
import time
import os
from datetime import datetime


def monitor_training(history_path='checkpoints/training_history.json', refresh_interval=10):
    """
    Monitor training progress via command line only
    Args:
        history_path: Path to training history JSON
        refresh_interval: Seconds between refreshes
    """
    print("\n" + "="*80)
    print("COMMAND-LINE TRAINING MONITOR".center(80))
    print("="*80)
    print(f"Monitoring: {history_path}")
    print(f"Refresh: Every {refresh_interval} seconds")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print("\nPress Ctrl+C to stop\n")
    
    last_epoch = -1
    
    try:
        while True:
            if not os.path.exists(history_path):
                print(f"\rWaiting for training to start...", end='', flush=True)
                time.sleep(refresh_interval)
                continue
            
            # Load history
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)
            except:
                time.sleep(refresh_interval)
                continue
            
            epochs = len(history['train']['g_loss'])
            
            if epochs == 0:
                print(f"\rNo epochs completed yet...", end='', flush=True)
                time.sleep(refresh_interval)
                continue
            
            current_epoch = epochs - 1
            
            # Only print when new epoch completes
            if current_epoch > last_epoch:
                last_epoch = current_epoch
                
                # Get metrics
                g_loss = history['train']['g_loss'][current_epoch]
                d_loss = history['train']['d_loss'][current_epoch]
                l1_loss = history['train']['l1_loss'][current_epoch]
                perc_loss = history['train']['perceptual_loss'][current_epoch]
                adv_loss = history['train']['adv_loss'][current_epoch]
                
                psnr = history['val']['psnr'][current_epoch]
                ssim = history['val']['ssim'][current_epoch]
                
                best_psnr = max(history['val']['psnr'])
                best_epoch = history['val']['psnr'].index(best_psnr)
                
                # Print update
                print("\n" + "="*80)
                print(f"EPOCH {current_epoch} COMPLETED".center(80))
                print("="*80)
                print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"\nTRAINING LOSSES:")
                print(f"  Generator:       {g_loss:8.4f}")
                print(f"  Discriminator:   {d_loss:8.4f}")
                print(f"  L1 (Pixel):      {l1_loss:8.4f}")
                print(f"  Perceptual:      {perc_loss:8.4f}")
                print(f"  Adversarial:     {adv_loss:8.4f}")
                print(f"\nVALIDATION METRICS:")
                print(f"  PSNR:  {psnr:6.4f} dB  {'🏆 NEW BEST!' if current_epoch == best_epoch else ''}")
                print(f"  SSIM:  {ssim:6.4f}")
                print(f"\nBEST SO FAR:")
                print(f"  Best PSNR: {best_psnr:.4f} dB (Epoch {best_epoch})")
                
                # Progress indicator
                improvement = psnr - history['val']['psnr'][current_epoch-1] if current_epoch > 0 else 0
                print(f"  Improvement from last epoch: {improvement:+.4f} dB")
                
                print("="*80)
            else:
                # Just show we're still monitoring
                print(f"\rMonitoring... (Last update: Epoch {current_epoch}, PSNR: {history['val']['psnr'][current_epoch]:.4f} dB)", end='', flush=True)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("MONITORING STOPPED".center(80))
        print("="*80)
        if last_epoch >= 0:
            print(f"Last completed epoch: {last_epoch}")
            print(f"Best PSNR: {best_psnr:.4f} dB at epoch {best_epoch}")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n\nError: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor training (command-line only)')
    parser.add_argument('--history_path', type=str, default='checkpoints/training_history.json',
                        help='Path to training history JSON')
    parser.add_argument('--refresh', type=int, default=10,
                        help='Refresh interval in seconds')
    
    args = parser.parse_args()
    
    monitor_training(args.history_path, args.refresh)
