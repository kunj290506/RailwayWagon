"""
Simple Command-Line Training Monitor
Shows all training stats in terminal without graphs
"""
import json
import time
import os
from datetime import datetime

def monitor_training(history_path='checkpoints/training_history.json', refresh_interval=3):
    """Print training progress to console"""
    print("="*80)
    print(" "*25 + "TRAINING MONITOR")
    print("="*80)
    print(f"Monitoring: {history_path}")
    print(f"Refresh: {refresh_interval}s | Press Ctrl+C to stop")
    print("="*80)
    
    last_epoch = -1
    
    try:
        while True:
            if not os.path.exists(history_path):
                print(f"\r⏳ Waiting for training to start...", end='', flush=True)
                time.sleep(refresh_interval)
                continue
            
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            if not history['train']['g_loss']:
                print(f"\r⏳ Waiting for first epoch...", end='', flush= True)
                time.sleep(refresh_interval)
                continue
            
            current_epoch = len(history['train']['g_loss'])
            
            # Only print when new epoch completes
            if current_epoch > last_epoch:
                last_epoch = current_epoch
                
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("="*80)
                print(f" "*30 + "TRAINING PROGRESS")
                print("="*80)
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Epoch: {current_epoch}/{200}")  # Assuming 200 epochs
                print("-"*80)
                
                # Latest epoch stats
                print("\n📊 Latest Epoch:")
                print(f"  Generator Loss:  {history['train']['g_loss'][-1]:.6f}")
                print(f"  Discriminator:   {history['train']['d_loss'][-1]:.6f}")
                print(f"  L1 Loss:         {history['train']['l1_loss'][-1]:.6f}")
                print(f"  Perceptual:      {history['train']['perceptual_loss'][-1]:.6f}")
                print(f"  Adversarial:     {history['train']['adv_loss'][-1]:.6f}")
                
                print("\n🎯 Validation Metrics:")
                psnr = history['val']['psnr'][-1]
                ssim = history['val']['ssim'][-1]
                print(f"  PSNR: {psnr:.4f} dB")
                print(f"  SSIM: {ssim:.4f}")
                
                # Best so far
                best_psnr = max(history['val']['psnr'])
                best_psnr_epoch = history['val']['psnr'].index(best_psnr) + 1
                best_ssim = max(history['val']['ssim'])
                
                print("\n🏆 Best Results:")
                print(f"  Best PSNR: {best_psnr:.4f} dB (Epoch {best_psnr_epoch})")
                print(f"  Best SSIM: {best_ssim:.4f}")
                
                # Progress bar
                progress = (current_epoch / 200) * 100
                bar_length = 50
                filled = int(bar_length * current_epoch / 200)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\n Progress: [{bar}] {progress:.1f}%")
                
                # Target indicator
                if best_psnr >= 32.0 and best_ssim >= 0.95:
                    print("\n✅ ALL TARGETS ACHIEVED!")
                    print(f"   PSNR: {best_psnr:.4f} dB ≥ 32.0 dB ✓")
                    print(f"   SSIM: {best_ssim:.4f} ≥ 0.95 ✓")
                elif best_psnr >= 32.0:
                    print(f"\n✅ PSNR TARGET ACHIEVED: {best_psnr:.4f} dB ≥ 32.0 dB")
                    ssim_remaining = 0.95 - best_ssim
                    print(f"🎯 SSIM Target: 0.95 | Remaining: +{ssim_remaining:.4f}")
                else:
                    psnr_remaining = 32.0 - best_psnr
                    ssim_remaining = 0.95 - best_ssim
                    print(f"\n🎯 Targets:")
                    print(f"   PSNR: 32.0 dB | Remaining: +{psnr_remaining:.2f} dB")
                    print(f"   SSIM: 0.95 | Remaining: +{ssim_remaining:.4f}")

                
                print("="*80)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', default='checkpoints/training_history.json')
    parser.add_argument('--refresh', type=int, default=3)
    args = parser.parse_args()
    
    monitor_training(args.history, args.refresh)
