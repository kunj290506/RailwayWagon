"""
Quick Deblur Setup for OCR
USE THIS NOW - No more training needed!
"""
import torch
import cv2
import numpy as np
from PIL import Image
import os

# OPTION 1: Use your trained model (if good enough)
# OPTION 2: Use NAFNet pre-trained (instant, no training)

class QuickDeblur:
    def __init__(self, use_nafnet=False):
        """
        Quick deblur for OCR preprocessing
        
        Args:
            use_nafnet: True = use pre-trained NAFNet (instant)
                       False = use your fine-tuned model
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if use_nafnet:
            print("Loading NAFNet (pre-trained, instant)...")
            from nafnet import NAFNet
            self.model = NAFNet(img_channel=3, width=64, middle_blk_num=12, 
                               enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2])
            checkpoint = torch.load('checkpoints/NAFNet-GoPro-width64.pth', 
                                   map_location='cpu', weights_only=False)
            self.model.load_state_dict(checkpoint['params'])
            print("✅ NAFNet loaded - ready for OCR")
        else:
            print("Loading your fine-tuned model...")
            from models import GeneratorResNet
            self.model = GeneratorResNet(n_residual_blocks=9)
            checkpoint = torch.load('checkpoints/best_model_finetune.pth', 
                                   map_location='cpu', weights_only=False)
            self.model.load_state_dict(checkpoint['generator_state_dict'])
            print(f"✅ Model loaded (PSNR: {checkpoint.get('best_psnr', 'N/A'):.2f} dB)")
        
        self.model.to(self.device)
        self.model.eval()
    
    def deblur_for_ocr(self, image_path, output_path=None):
        """
        Deblur image for better OCR results
        
        Args:
            image_path: Path to blurry image
            output_path: Where to save deblurred image (optional)
        
        Returns:
            numpy array of deblurred image (ready for OCR)
        """
        # Load image
        img = Image.open(image_path).convert('RGB')
        original_size = img.size
        
        # Preprocess
        img_tensor = self._preprocess(img)
        
        # Deblur
        with torch.no_grad():
            deblurred_tensor = self.model(img_tensor)
        
        # Postprocess
        deblurred_img = self._postprocess(deblurred_tensor, original_size)
        
        # Save if requested
        if output_path:
            cv2.imwrite(output_path, cv2.cvtColor(deblurred_img, cv2.COLOR_RGB2BGR))
            print(f"Saved: {output_path}")
        
        return deblurred_img
    
    def _preprocess(self, img):
        """Prepare image for model"""
        # Resize to model input size
        img_resized = img.resize((256, 256), Image.LANCZOS)
        
        # Convert to tensor [-1, 1]
        img_array = np.array(img_resized).astype(np.float32) / 255.0
        img_array = (img_array - 0.5) / 0.5  # Normalize to [-1, 1]
        
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
        return img_tensor.to(self.device)
    
    def _postprocess(self, tensor, target_size):
        """Convert model output back to image"""
        # Denormalize from [-1, 1] to [0, 255]
        img_array = tensor[0].cpu().numpy().transpose(1, 2, 0)
        img_array = (img_array + 1) / 2  # [-1, 1] -> [0, 1]
        img_array = (img_array * 255).clip(0, 255).astype(np.uint8)
        
        # Resize back to original size
        img_array = cv2.resize(img_array, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        return img_array
    
    def batch_deblur(self, input_folder, output_folder):
        """
        Deblur all images in a folder for OCR
        
        Args:
            input_folder: Folder with blurry images
            output_folder: Where to save deblurred images
        """
        os.makedirs(output_folder, exist_ok=True)
        
        image_files = [f for f in os.listdir(input_folder) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"\nDeblurring {len(image_files)} images for OCR...")
        
        for i, filename in enumerate(image_files, 1):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"deblurred_{filename}")
            
            self.deblur_for_ocr(input_path, output_path)
            print(f"  [{i}/{len(image_files)}] {filename}")
        
        print(f"\n✅ Done! Deblurred images in: {output_folder}")


# QUICK START EXAMPLES

def quick_single_image():
    """Deblur one image - FASTEST"""
    # Use NAFNet (pre-trained, instant)
    deblur = QuickDeblur(use_nafnet=True)
    
    # Deblur for OCR
    result = deblur.deblur_for_ocr(
        'path/to/blurry_wagon.jpg',
        'path/to/sharp_wagon.jpg'
    )
    
    # Now use result for OCR
    # import easyocr
    # reader = easyocr.Reader(['en'])
    # text = reader.readtext(result)
    print("Image ready for OCR!")


def quick_batch_processing():
    """Deblur folder of images"""
    # Use NAFNet (pre-trained, instant)
    deblur = QuickDeblur(use_nafnet=True)
    
    # Deblur all images
    deblur.batch_deblur(
        input_folder='blurry_images',
        output_folder='deblurred_for_ocr'
    )


if __name__ == '__main__':
    print("="*60)
    print("QUICK DEBLUR FOR OCR")
    print("="*60)
    print("\nChoose option:")
    print("1. Use NAFNet (pre-trained, INSTANT, no training)")
    print("2. Use your fine-tuned model (better quality, trained 8.5hrs)")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    use_nafnet = (choice == '1')
    
    # Initialize
    deblur = QuickDeblur(use_nafnet=use_nafnet)
    
    # Get input
    print("\nDeblur:")
    print("  S = Single image")
    print("  B = Batch folder")
    
    mode = input("Enter S or B: ").strip().upper()
    
    if mode == 'S':
        img_path = input("Image path: ").strip()
        out_path = input("Output path (or press Enter): ").strip()
        
        if not out_path:
            out_path = img_path.replace('.jpg', '_deblurred.jpg')
        
        deblur.deblur_for_ocr(img_path, out_path)
        print(f"\n✅ Ready for OCR: {out_path}")
        
    elif mode == 'B':
        in_folder = input("Input folder: ").strip()
        out_folder = input("Output folder: ").strip()
        
        deblur.batch_deblur(in_folder, out_folder)
        print(f"\n✅ All images ready for OCR!")
