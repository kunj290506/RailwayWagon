"""
Download NAFNet Pre-trained Model
Model: NAFNet-GoPro-width64
Performance: 33.7 dB PSNR, 0.967 SSIM
"""

import gdown
import os

# NAFNet-GoPro-width64 Google Drive ID
# From: https://github.com/megvii-research/NAFNet
model_url = "https://drive.google.com/uc?id=14Fht1QQJ2gMlk4N1ERCRuElg8JfjrWWR"
output_path = "checkpoints/NAFNet-GoPro-width64.pth"

os.makedirs("checkpoints", exist_ok=True)

print("Downloading NAFNet pre-trained model...")
print(f"Target: {output_path}")
print("Performance: 33.7 dB PSNR, 0.967 SSIM")

gdown.download(model_url, output_path, quiet=False)

print("\n✅ Download complete!")
print(f"Model saved to: {output_path}")
