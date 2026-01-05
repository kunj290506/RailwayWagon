import torch
from torch.utils.data import DataLoader
from dataset import DeblurDataset, PairedTransform
from models import GeneratorResNet
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
import numpy as np
import glob
import os

def evaluate(checkpoint_path, num_samples=100):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Initialize generator and load checkpoint
    generator = GeneratorResNet().to(device)
    
    if os.path.exists(checkpoint_path):
        generator.load_state_dict(torch.load(checkpoint_path))
        print(f"Loaded checkpoint from {checkpoint_path}")
    else:
        print(f"Checkpoint not found at {checkpoint_path}")
        return
    
    generator.eval()

    # Dataset
    root_dir = r"C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp"
    dataset = DeblurDataset(root_dir=root_dir)
    transform = PairedTransform(size=256)
    
    dataloader = DataLoader(
        dataset, 
        batch_size=1, 
        shuffle=False, 
        num_workers=0,
        collate_fn=lambda x: list(zip(*x))
    )

    psnr_scores = []
    ssim_scores = []
    
    print(f"Evaluating on {min(num_samples, len(dataset))} samples...")
    
    with torch.no_grad():
        for i, (imgs_blur, imgs_sharp) in enumerate(dataloader):
            if i >= num_samples:
                break
                
            # Transform
            blur_img, sharp_img = imgs_blur[0], imgs_sharp[0]
            blur_tensor, sharp_tensor = transform(blur_img, sharp_img)
            blur_tensor = blur_tensor.unsqueeze(0).to(device)
            sharp_tensor = sharp_tensor.unsqueeze(0).to(device)
            
            # Generate
            generated = generator(blur_tensor)
            
            # Convert to numpy for metrics (denormalize from [-1, 1] to [0, 1])
            generated_np = ((generated[0].cpu().numpy().transpose(1, 2, 0) + 1) / 2).clip(0, 1)
            sharp_np = ((sharp_tensor[0].cpu().numpy().transpose(1, 2, 0) + 1) / 2).clip(0, 1)
            
            # Calculate metrics
            psnr_val = psnr(sharp_np, generated_np, data_range=1.0)
            ssim_val = ssim(sharp_np, generated_np, data_range=1.0, channel_axis=2)
            
            psnr_scores.append(psnr_val)
            ssim_scores.append(ssim_val)
            
            if (i + 1) % 20 == 0:
                print(f"  Processed {i+1}/{num_samples} images...")
    
    # Calculate averages
    avg_psnr = np.mean(psnr_scores)
    avg_ssim = np.mean(ssim_scores)
    
    print("\n" + "="*50)
    print(f"EVALUATION RESULTS")
    print("="*50)
    print(f"Average PSNR: {avg_psnr:.2f} dB")
    print(f"Average SSIM: {avg_ssim:.4f}")
    print("="*50)
    print("\nInterpretation:")
    print("  PSNR > 30 dB: Good quality")
    print("  PSNR > 35 dB: Excellent quality")
    print("  SSIM > 0.90: Very good structural similarity")
    print("  SSIM > 0.95: Excellent structural similarity")
    
    return avg_psnr, avg_ssim

if __name__ == "__main__":
    # Find the latest checkpoint
    checkpoints = glob.glob("checkpoints/generator_*.pth")
    if checkpoints:
        latest_checkpoint = max(checkpoints, key=os.path.getctime)
        print(f"Evaluating checkpoint: {latest_checkpoint}\n")
        evaluate(latest_checkpoint, num_samples=100)
    else:
        print("No checkpoints found!")
