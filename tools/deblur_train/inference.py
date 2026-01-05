"""
Enhanced Inference Script for Image Deblurring
Supports single image, batch processing, and quality metrics
"""
import torch
from PIL import Image
import torchvision.transforms as transforms
import argparse
import os
from pathlib import Path
import time
from tqdm import tqdm

from models import GeneratorResNet
from config import Config
from utils import calculate_psnr, calculate_ssim, denormalize


def load_model(checkpoint_path, device='cuda'):
    """Load trained generator model"""
    config = Config()
    
    generator = GeneratorResNet(
        in_channels=config.IN_CHANNELS,
        out_channels=config.OUT_CHANNELS,
        n_residual_blocks=config.N_RESIDUAL_BLOCKS
    ).to(device)
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    generator.load_state_dict(checkpoint['generator_state_dict'])
    generator.eval()
    
    print(f"Model loaded from {checkpoint_path}")
    if 'epoch' in checkpoint:
        print(f"Checkpoint epoch: {checkpoint['epoch']}")
    if 'best_psnr' in checkpoint:
        print(f"Checkpoint PSNR: {checkpoint['best_psnr']:.4f} dB")
    
    return generator


def get_transform(img_size=256):
    """Get image transformation pipeline"""
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])


def deblur_image(generator, image_path, output_path, device='cuda', img_size=256):
    """Deblur a single image"""
    transform = get_transform(img_size)
    
    # Load and preprocess image
    img = Image.open(image_path).convert('RGB')
    original_size = img.size
    
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    # Generate deblurred image
    with torch.no_grad():
        deblurred_tensor = generator(img_tensor)
    
    # Denormalize and convert to PIL
    deblurred_tensor = denormalize(deblurred_tensor)
    deblurred_img = transforms.ToPILImage()(deblurred_tensor.squeeze(0).cpu())
    
    # Resize back to original size
    deblurred_img = deblurred_img.resize(original_size, Image.LANCZOS)
    
    # Save
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    deblurred_img.save(output_path)
    
    return deblurred_img


def batch_deblur(generator, input_dir, output_dir, device='cuda', img_size=256, compare_with_gt=None):
    """Deblur all images in a directory"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in Path(input_dir).iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    print(f"\nProcessing {len(image_files)} images from {input_dir}")
    print(f"Output directory: {output_dir}\n")
    
    transform = get_transform(img_size)
    total_time = 0
    
    # For calculating metrics if ground truth provided
    metrics = {'psnr': [], 'ssim': []} if compare_with_gt else None
    
    for img_file in tqdm(image_files, desc="Deblurring"):
        start_time = time.time()
        
        # Load and process image
        img = Image.open(img_file).convert('RGB')
        original_size = img.size
        
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        # Generate deblurred image
        with torch.no_grad():
            deblurred_tensor = generator(img_tensor)
        
        # Denormalize and convert to PIL
        deblurred_tensor_denorm = denormalize(deblurred_tensor)
        deblurred_img = transforms.ToPILImage()(deblurred_tensor_denorm.squeeze(0).cpu())
        deblurred_img = deblurred_img.resize(original_size, Image.LANCZOS)
        
        # Save
        output_path = os.path.join(output_dir, img_file.name)
        deblurred_img.save(output_path)
        
        # Calculate metrics if ground truth provided
        if compare_with_gt:
            gt_path = os.path.join(compare_with_gt, img_file.name)
            if os.path.exists(gt_path):
                gt_img = Image.open(gt_path).convert('RGB')
                gt_tensor = transform(gt_img).unsqueeze(0).to(device)
                
                psnr = calculate_psnr(deblurred_tensor, gt_tensor)
                ssim = calculate_ssim(deblurred_tensor, gt_tensor)
                
                metrics['psnr'].append(psnr)
                metrics['ssim'].append(ssim)
        
        total_time += time.time() - start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Total images: {len(image_files)}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per image: {total_time/len(image_files):.3f}s")
    
    if metrics and metrics['psnr']:
        print(f"\nQuality Metrics:")
        print(f"  Average PSNR: {sum(metrics['psnr'])/len(metrics['psnr']):.4f} dB")
        print(f"  Average SSIM: {sum(metrics['ssim'])/len(metrics['ssim']):.4f}")
    
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Deblur images using trained model')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best_model.pth',
                        help='Path to model checkpoint')
    parser.add_argument('--input', type=str, required=True,
                        help='Input image path or directory')
    parser.add_argument('--output', type=str, required=True,
                        help='Output image path or directory')
    parser.add_argument('--batch', action='store_true',
                        help='Batch mode: process entire directory')
    parser.add_argument('--compare_with', type=str, default=None,
                        help='Ground truth directory for metric calculation (batch mode only)')
    parser.add_argument('--img_size', type=int, default=256,
                        help='Image size for processing')
    parser.add_argument('--device', type=str, default='cuda',
                        help='Device to use (cuda or cpu)')
    
    args = parser.parse_args()
    
    # Check device availability
    device = args.device if torch.cuda.is_available() else 'cpu'
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
    
    print("="*60)
    print("IMAGE DEBLURRING INFERENCE")
    print("="*60)
    print(f"Device: {device}")
    print(f"Checkpoint: {args.checkpoint}")
    print("="*60)
    
    # Load model
    generator = load_model(args.checkpoint, device)
    
    # Process
    if args.batch:
        batch_deblur(generator, args.input, args.output, device, args.img_size, args.compare_with)
    else:
        print(f"\nDeblurring: {args.input}")
        start_time = time.time()
        deblur_image(generator, args.input, args.output, device, args.img_size)
        elapsed = time.time() - start_time
        print(f"Saved to: {args.output}")
        print(f"Time: {elapsed:.3f}s")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
