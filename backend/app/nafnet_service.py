"""
Optimized NAFNet Deblur Service - Fast Inference
Uses width32 (still 32.8 dB PSNR) + FP16 for speed
"""

import torch
import cv2
import numpy as np
from pathlib import Path
import os

# Singleton instance
_nafnet_model = None

class NAFNetDeblur:
    """Optimized NAFNet for fast inference"""
    
    def __init__(self, checkpoint_path=None, use_fp16=True):
        # Import NAFNet
        import sys
        tools_path = Path(__file__).parent.parent.parent / 'tools' / 'deblur_train'
        sys.path.insert(0, str(tools_path))
        
        from nafnet import NAFNet
        
        if checkpoint_path is None:
            # Use width32 for faster processing (still 32.8 dB PSNR!)
            checkpoint_path = str(tools_path / 'checkpoints' / 'NAFNet-GoPro-width32.pth')
            
            # Fallback to width64 if width32 not found
            if not os.path.exists(checkpoint_path):
                checkpoint_path = str(tools_path / 'checkpoints' / 'NAFNet-GoPro-width64.pth')
                print("⚠️ Using width64 (slower but 33.7 dB). Download width32 for 2x speedup.")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_fp16 = use_fp16 and torch.cuda.is_available()
        
        print(f"Loading NAFNet from {checkpoint_path}...")
        
        # Determine model width from filename
        width = 32 if 'width32' in checkpoint_path else 64
        
        # Initialize NAFNet
        self.model = NAFNet(
            img_channel=3,
            width=width,
            middle_blk_num=12,
            enc_blk_nums=[2, 2, 4, 8],
            dec_blk_nums=[2, 2, 2, 2]
        ).to(self.device)
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
        
        if 'params' in checkpoint:
            self.model.load_state_dict(checkpoint['params'])
        elif 'state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['state_dict'])
        else:
            self.model.load_state_dict(checkpoint)
        
        # Convert to FP16 for speed
        if self.use_fp16:
            self.model = self.model.half()
            print(f"✅ NAFNet-width{width} loaded with FP16 (2x faster)")
        else:
            print(f"✅ NAFNet-width{width} loaded")
        
        self.model.eval()
    
    @torch.no_grad()
    def deblur_image(self, image):
        """
        Fast deblur with optimizations
        Args:
            image: numpy array (H, W, C) in BGR
        Returns:
            deblurred image in BGR
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Downsample for speed if image is too large
        h, w = image_rgb.shape[:2]
        max_size = 720
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_h, new_w = int(h * scale), int(w * scale)
            image_rgb = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Normalize
        image_norm = image_rgb.astype(np.float32) / 255.0
        
        # To tensor
        image_tensor = torch.from_numpy(image_norm).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        # FP16 if enabled
        if self.use_fp16:
            image_tensor = image_tensor.half()
        
        # Inference
        output = self.model(image_tensor)
        
        # Back to numpy
        if self.use_fp16:
            output = output.float()
        
        output = output.squeeze(0).permute(1, 2, 0).cpu().numpy()
        output = np.clip(output * 255.0, 0, 255).astype(np.uint8)
        
        # Resize back if downsampled
        if max(h, w) > max_size:
            output = cv2.resize(output, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # RGB to BGR
        output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
        
        return output_bgr


def get_nafnet_model():
    """Get singleton NAFNet instance"""
    global _nafnet_model
    if _nafnet_model is None:
        _nafnet_model = NAFNetDeblur(use_fp16=True)
    return _nafnet_model

