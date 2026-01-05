"""
LIVE Real-Time Training Monitor - Visible Updates
Shows training progress updating every few seconds in your command window
"""
import json
import time
import os
from datetime import datetime


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def live_monitor(history_path='checkpoints/training_history.json', refresh_interval=5):
    """
    Live monitoring with visible real-time updates
    """
    print("Starting Live Training Monitor...")
    print("Loading training data...")
    time.sleep(2)
    
    last_epoch = -1
    iterations = 0
    
    try:
        while True:
            iterations += 1
            
            # Clear screen for fresh display
            if iterations > 1:
                clear_screen()
            
            # Print header
            print("\n" + "="*80)
            print("🚀 LIVE TRAINING MONITOR - REAL-TIME UPDATES".center(80))
            print("="*80)
            print(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")
            print(f"🔄 Refresh: Every {refresh_interval} seconds")
            print("="*80 + "\n")
            
            # Check if file exists
            if not os.path.exists(history_path):
                print("⏳ WAITING FOR TRAINING TO START...")
                print(f"   Looking for: {history_path}")
                print(f"   Checked {iterations} times")
                print("\n" + "="*80)
                time.sleep(refresh_interval)
                continue
            
            # Load history
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                print(f"⚠️  Error reading history file: {e}")
                print("   Retrying...")
                time.sleep(refresh_interval)
                continue
            
            # Check if we have data
            if not history.get('train', {}).get('g_loss'):
                print("⏳ TRAINING STARTED - Waiting for first epoch...")
                print("\n" + "="*80)
                time.sleep(refresh_interval)
                continue
            
            # Get current epoch
            total_epochs = len(history['train']['g_loss'])
            current_epoch = total_epochs - 1
            
            # Get latest metrics
            g_loss = history['train']['g_loss'][current_epoch]
            d_loss = history['train']['d_loss'][current_epoch]
            l1_loss = history['train']['l1_loss'][current_epoch]
            perc_loss = history['train']['perceptual_loss'][current_epoch]
            adv_loss = history['train']['adv_loss'][current_epoch]
            
            psnr = history['val']['psnr'][current_epoch]
            ssim = history['val']['ssim'][current_epoch]
            
            # Calculate bests
            best_psnr = max(history['val']['psnr'])
            best_psnr_epoch = history['val']['psnr'].index(best_psnr)
            best_ssim = max(history['val']['ssim'])
            
            # Show progress
            print("📊 TRAINING PROGRESS")
            print("-" * 80)
            print(f"   Current Epoch: {current_epoch} / 150")
            progress_pct = (current_epoch / 150) * 100
            progress_bar = "█" * int(progress_pct / 2) + "░" * (50 - int(progress_pct / 2))
            print(f"   Progress: [{progress_bar}] {progress_pct:.1f}%")
            print()
            
            # Training Losses
            print("🔥 TRAINING LOSSES (Latest Epoch)")
            print("-" * 80)
            print(f"   Generator Loss:      {g_loss:10.6f}")
            print(f"   Discriminator Loss:  {d_loss:10.6f}")
            print(f"   L1 Loss (Pixel):     {l1_loss:10.6f}")
            print(f"   Perceptual Loss:     {perc_loss:10.6f}")
            print(f"   Adversarial Loss:    {adv_loss:10.6f}")
            print()
            
            # Validation Metrics
            print("✨ VALIDATION METRICS (Latest Epoch)")
            print("-" * 80)
            is_best = (current_epoch == best_psnr_epoch)
            print(f"   PSNR:  {psnr:8.4f} dB  {'🏆 BEST!' if is_best else ''}")
            print(f"   SSIM:  {ssim:8.4f}")
            print()
            
            # Best So Far
            print("🏆 BEST RESULTS SO FAR")
            print("-" * 80)
            print(f"   Best PSNR:  {best_psnr:.4f} dB (Epoch {best_psnr_epoch})")
            print(f"   Best SSIM:  {best_ssim:.4f}")
            
            # Improvement tracking
            if current_epoch > 0:
                prev_psnr = history['val']['psnr'][current_epoch - 1]
                improvement = psnr - prev_psnr
                print(f"   Last Change: {improvement:+.4f} dB")
            
            print()
            
            # Epochs without improvement
            epochs_since_best = current_epoch - best_psnr_epoch
            if epochs_since_best > 0:
                print(f"⚠️  {epochs_since_best} epochs since best PSNR")
                if epochs_since_best >= 20:
                    print(f"   ⚠️  Training may stop soon (early stopping patience: 30)")
            
            print("\n" + "="*80)
            print(f"Next update in {refresh_interval} seconds... (Press Ctrl+C to stop)")
            print("="*80)
            
            # Check if new epoch completed
            if current_epoch > last_epoch:
                last_epoch = current_epoch
                # Beep to alert user
                print('\a')  # Terminal bell
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n" + "="*80)
        print("🛑 MONITORING STOPPED BY USER".center(80))
        print("="*80)
        if last_epoch >= 0:
            print(f"\nFinal Status:")
            print(f"  Last Epoch: {last_epoch}")
            print(f"  Best PSNR: {best_psnr:.4f} dB (Epoch {best_psnr_epoch})")
            print(f"  Best SSIM: {best_ssim:.4f}")
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Training Monitor with Visible Updates')
    parser.add_argument('--history_path', type=str, default='checkpoints/training_history.json',
                        help='Path to training history JSON')
    parser.add_argument('--refresh', type=int, default=5,
                        help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    live_monitor(args.history_path, args.refresh)
