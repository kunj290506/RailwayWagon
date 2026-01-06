"""
Deblur Service - Uses trained deblurring model (29.08 dB PSNR)
Replaces Zero-DCE for better frame quality and OCR accuracy
"""
import torch
import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import os

# Import exact model architecture from training
from app.deblur_models import GeneratorResNet



class DeblurModel:
    """Wrapper for trained deblurring model"""
    
    def __init__(self, checkpoint_path=None):
        """Load the trained model"""
        # Default path from backend/app directory
        if checkpoint_path is None:
            app_dir = os.path.dirname(os.path.abspath(__file__))  # backend/app
            backend_dir = os.path.dirname(app_dir)  # backend
            project_root = os.path.dirname(backend_dir)  # project root (adani)
            checkpoint_path = os.path.join(project_root, 'tools', 'deblur_train', 'checkpoints', 'best_model.pth')
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"Loading deblurring model from {checkpoint_path}...")
        
        # Initialize generator with same config as training
        self.generator = GeneratorResNet(
            in_channels=3,
            out_channels=3,
            n_residual_blocks=12
        ).to(self.device)
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.generator.load_state_dict(checkpoint['generator_state_dict'])
        self.generator.eval()
        
        best_psnr = checkpoint.get('best_psnr', 'Unknown')
        print(f"Deblur model loaded successfully! Performance: {best_psnr} dB PSNR")
        
        # Transform for model input
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
    
    def deblur_image(self, image):
        """
        Deblur a single image
        Args:
            image: numpy array (BGR) or PIL Image
        Returns:
            numpy array (BGR) - deblurred image
        """
        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        original_size = image.size
        
        # Preprocess
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Deblur
        with torch.no_grad():
            deblurred_tensor = self.generator(img_tensor)
        
        # Denormalize from [-1, 1] to [0, 1]
        deblurred_tensor = (deblurred_tensor + 1) / 2.0
        deblurred_tensor = torch.clamp(deblurred_tensor, 0, 1)
        
        # Convert to PIL
        deblurred_img = transforms.ToPILImage()(deblurred_tensor.squeeze(0).cpu())
        
        # Resize back to original size
        deblurred_img = deblurred_img.resize(original_size, Image.LANCZOS)
        
        # Convert to cv2 format (BGR)
        deblurred_cv2 = cv2.cvtColor(np.array(deblurred_img), cv2.COLOR_RGB2BGR)
        
        return deblurred_cv2


# Global model instance
_deblur_model = None

def get_deblur_model():
    """Get singleton instance of deblur model"""
    global _deblur_model
    if _deblur_model is None:
        _deblur_model = DeblurModel()
    return _deblur_model
