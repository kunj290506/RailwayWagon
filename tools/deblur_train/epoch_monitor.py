"""
Epoch Monitor with Time Remaining
Shows epoch info and estimates remaining time
"""
import json
import time
import os
from datetime import datetime, timedelta


def monitor_epochs(history_path='checkpoints/training_history.json'):
    """
    Monitor that shows epoch completion with time estimates
    """
    print("\n" + "="*80)
    print("EPOCH MONITOR WITH TIME TRACKING")
    print("="*80)
    print("Prints info when each epoch completes.")
    print("="*80 + "\n")
    
    last_epoch = -1
    epoch_times = []
    start_time = time.time()
    last_epoch_time = time.time()
    
    try:
        while True:
            if not os.path.exists(history_path):
                time.sleep(5)
                continue
            
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)
            except:
                time.sleep(5)
                continue
            
            if not history.get('train', {}).get('g_loss'):
                time.sleep(5)
                continue
            
            current_epoch = len(history['train']['g_loss']) - 1
            total_epochs = 150  # From config
            
            # Only print when NEW epoch completes
            if current_epoch > last_epoch:
                # Calculate epoch time
                epoch_duration = time.time() - last_epoch_time
                if last_epoch >= 0:  # Don't count first epoch timing
                    epoch_times.append(epoch_duration)
                last_epoch_time = time.time()
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
                
                # Calculate time estimates
                elapsed_total = time.time() - start_time
                elapsed_hours = elapsed_total / 3600
                
                if epoch_times:
                    avg_epoch_time = sum(epoch_times) / len(epoch_times)
                    remaining_epochs = total_epochs - current_epoch - 1
                    estimated_remaining_seconds = avg_epoch_time * remaining_epochs
                    estimated_remaining_hours = estimated_remaining_seconds / 3600
                    
                    eta_timestamp = datetime.now() + timedelta(seconds=estimated_remaining_seconds)
                    eta_str = eta_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    avg_epoch_time = 0
                    estimated_remaining_hours = 0
                    eta_str = "Calculating..."
                
                # Print epoch info
                print("\n" + "="*80)
                print(f"EPOCH {current_epoch} COMPLETED")
                print("="*80)
                
                # Time info
                print("\nTIME INFORMATION:")
                print(f"  Elapsed:          {elapsed_hours:.2f} hours")
                if epoch_times:
                    print(f"  Avg per epoch:    {avg_epoch_time/60:.1f} minutes")
                    print(f"  Est. remaining:   {estimated_remaining_hours:.1f} hours")
                    print(f"  ETA:              {eta_str}")
                print(f"  Progress:         {current_epoch+1}/{total_epochs} ({((current_epoch+1)/total_epochs*100):.1f}%)")
                
                print("\nTRAINING LOSSES:")
                print(f"  Generator:       {g_loss:.6f}")
                print(f"  Discriminator:   {d_loss:.6f}")
                print(f"  L1 (Pixel):      {l1_loss:.6f}")
                print(f"  Perceptual:      {perc_loss:.6f}")
                print(f"  Adversarial:     {adv_loss:.6f}")
                
                print("\nVALIDATION METRICS:")
                is_best = (current_epoch == best_epoch)
                print(f"  PSNR:  {psnr:.4f} dB  {'[BEST]' if is_best else ''}")
                print(f"  SSIM:  {ssim:.4f}")
                
                print("\nBEST RESULTS:")
                print(f"  Best PSNR: {best_psnr:.4f} dB (Epoch {best_epoch})")
                
                if current_epoch > 0:
                    prev_psnr = history['val']['psnr'][current_epoch - 1]
                    improvement = psnr - prev_psnr
                    print(f"  Change from previous: {improvement:+.4f} dB")
                
                epochs_since_best = current_epoch - best_epoch
                if epochs_since_best > 0:
                    print(f"\nEpochs without improvement: {epochs_since_best}/30")
                
                print("="*80)
                print(f"Waiting for epoch {current_epoch + 1}...")
                print("="*80 + "\n")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n" + "="*80)
        print("MONITORING STOPPED")
        print("="*80)
        if last_epoch >= 0:
            print(f"Last epoch: {last_epoch}")
            print(f"Best PSNR: {best_psnr:.4f} dB (Epoch {best_epoch})")
            if epoch_times:
                print(f"Average epoch time: {sum(epoch_times)/len(epoch_times)/60:.1f} minutes")
        print("="*80 + "\n")


if __name__ == '__main__':
    monitor_epochs()
