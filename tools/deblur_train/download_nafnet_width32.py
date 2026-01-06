"""
Download NAFNet-width32 (Faster model)
Performance: 32.8 dB PSNR, 0.961 SSIM
~2x faster than width64
"""

import gdown
import os

# NAFNet-GoPro-width32 Google Drive ID
model_url = "https://drive.google.com/uc?id=1Fr2QadtDCEXg6iwWX8OzeZLbHOx2t5Bh"
output_path = "checkpoints/NAFNet-GoPro-width32.pth"

os.makedirs("checkpoints", exist_ok=True)

print("Downloading NAFNet-width32 (faster model)...")
print(f"Target: {output_path}")
print("Performance: 32.8 dB PSNR, 0.961 SSIM")
print("Speed: ~2x faster than width64")

gdown.download(model_url, output_path, quiet=False)

print("\n✅ Download complete!")
print(f"Model saved to: {output_path}")
