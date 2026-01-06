"""
PRODUCTION-READY: Deblur + Best OCR Pipeline
Optimized for Railway Wagon Number Extraction
"""
import torch
import cv2
import numpy as np
from PIL import Image
import os
import re
from typing import List, Tuple, Dict


class WagonNumberOCR:
    """
    Complete pipeline: Deblur → OCR → Extract Wagon Numbers
    Optimized for maximum accuracy
    """
    
    def __init__(self, use_gpu=True, mode='wagon'):
        """
        Initialize deblur + OCR pipeline
        
        Args:
            use_gpu: Use GPU for faster processing
            mode: 'wagon' = detect wagon numbers (11-digit rule)
                  'normal' = detect all meaningful text
        """
        print("🚀 Initializing Wagon Number OCR Pipeline...")
        
        self.device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
        self.mode = mode.lower()
        print(f"   Device: {self.device}")
        print(f"   Mode: {self.mode.upper()}")
        
        # 1. Load NAFNet Deblur Model (instant, pre-trained)
        self._load_deblur_model()
        
        # 2. Load Best OCR Model
        self._load_ocr_model()
        
        print("✅ Pipeline ready!\n")
    
    def _load_deblur_model(self):
        """Load NAFNet for deblurring"""
        print("   Loading NAFNet deblur model...")
        try:
            from nafnet import NAFNet
            
            self.deblur_model = NAFNet(
                img_channel=3, 
                width=64, 
                middle_blk_num=12,
                enc_blk_nums=[2, 2, 4, 8], 
                dec_blk_nums=[2, 2, 2, 2]
            )
            
            checkpoint_path = 'checkpoints/NAFNet-GoPro-width64.pth'
            if os.path.exists(checkpoint_path):
                checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
                self.deblur_model.load_state_dict(checkpoint['params'])
                self.deblur_model.to(self.device)
                self.deblur_model.eval()
                print("   ✓ NAFNet loaded")
            else:
                print(f"   ⚠ NAFNet not found at {checkpoint_path}")
                print("   → Will skip deblurring step")
                self.deblur_model = None
        except Exception as e:
            print(f"   ⚠ Deblur model loading failed: {e}")
            self.deblur_model = None
    
    def _load_ocr_model(self):
        """Load best OCR model for wagon numbers"""
        print("   Loading OCR model...")
        
        # Try PaddleOCR first (best for industrial text)
        try:
            from paddleocr import PaddleOCR
            
            # PaddleOCR auto-detects GPU in newer versions
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # Auto-rotate text
                lang='en'            # English + numbers
            )
            self.ocr_type = 'paddle'
            print(f"   ✓ PaddleOCR loaded (using {self.device})")
            
        except ImportError:
            # Fallback to EasyOCR
            try:
                import easyocr
                
                self.ocr = easyocr.Reader(
                    ['en'],
                    gpu=(self.device.type == 'cuda'),
                    verbose=False
                )
                self.ocr_type = 'easy'
                print("   ✓ EasyOCR loaded")
                
            except ImportError:
                # Ultimate fallback: Tesseract
                try:
                    import pytesseract
                    self.ocr = pytesseract
                    self.ocr_type = 'tesseract'
                    print("   ✓ Tesseract loaded")
                except:
                    raise RuntimeError(
                        "No OCR engine found! Install one:\n"
                        "  pip install paddleocr   (RECOMMENDED)\n"
                        "  pip install easyocr     (Good)\n"
                        "  pip install pytesseract (Basic)"
                    )
    
    def process_image(self, image_path: str, save_debug=False) -> Dict:
        """
        Complete pipeline: Deblur → OCR → Extract wagon numbers
        
        Args:
            image_path: Path to image
            save_debug: Save intermediate images for debugging
        
        Returns:
            {
                'wagon_numbers': ['ABC123', 'XYZ789'],  # Found wagon numbers
                'all_text': 'ABC123 WAGON XYZ789',      # All detected text
                'confidence': 0.95,                     # Overall confidence
                'deblurred_image': np.array,            # Deblurred image
                'detections': [...]                     # Raw OCR detections
            }
        """
        result = {
            'wagon_numbers': [],
            'all_text': '',
            'confidence': 0.0,
            'deblurred_image': None,
            'detections': []
        }
        
        # Step 1: Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Step 2: Deblur (if model available)
        if self.deblur_model is not None:
            deblurred = self._deblur_image(img)
            result['deblurred_image'] = deblurred
            
            if save_debug:
                debug_path = image_path.replace('.jpg', '_deblurred.jpg')
                cv2.imwrite(debug_path, deblurred)
        else:
            deblurred = img
            result['deblurred_image'] = img
        
        # Step 3: Preprocessing for better OCR
        processed = self._preprocess_for_ocr(deblurred)
        
        if save_debug:
            debug_path = image_path.replace('.jpg', '_processed.jpg')
            cv2.imwrite(debug_path, processed)
        
        # Step 4: OCR
        detections = self._run_ocr(processed)
        result['detections'] = detections
        
        # Step 5: Extract wagon numbers
        wagon_numbers, all_text, confidence = self._extract_wagon_numbers(detections)
        
        result['wagon_numbers'] = wagon_numbers
        result['all_text'] = all_text
        result['confidence'] = confidence
        
        return result
    
    def _deblur_image(self, img: np.ndarray) -> np.ndarray:
        """Deblur image using NAFNet"""
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]
        
        # Resize to model input size
        img_resized = cv2.resize(img_rgb, (256, 256), interpolation=cv2.INTER_LINEAR)
        
        # Normalize to [0, 1]
        img_tensor = torch.from_numpy(img_resized).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        # Deblur
        with torch.no_grad():
            deblurred_tensor = self.deblur_model(img_tensor)
        
        # Convert back to image
        deblurred = deblurred_tensor[0].cpu().numpy().transpose(1, 2, 0)
        deblurred = (deblurred * 255).clip(0, 255).astype(np.uint8)
        
        # Resize back to original size
        deblurred = cv2.resize(deblurred, (w, h), interpolation=cv2.INTER_CUBIC)
        
        # Convert RGB back to BGR
        return cv2.cvtColor(deblurred, cv2.COLOR_RGB2BGR)
    
    def _preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing for better OCR accuracy
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding for better contrast
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, h=10)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        return sharpened
    
    def _run_ocr(self, img: np.ndarray) -> List:
        """Run OCR on preprocessed image"""
        detections = []
        
        if self.ocr_type == 'paddle':
            # PaddleOCR
            results = self.ocr.ocr(img, cls=True)
            
            if results and results[0]:
                for detection in results[0]:
                    box, (text, conf) = detection
                    detections.append({
                        'text': text.upper().strip(),
                        'confidence': float(conf),
                        'box': box
                    })
        
        elif self.ocr_type == 'easy':
            # EasyOCR
            results = self.ocr.readtext(img)
            
            for (box, text, conf) in results:
                detections.append({
                    'text': text.upper().strip(),
                    'confidence': float(conf),
                    'box': box
                })
        
        elif self.ocr_type == 'tesseract':
            # Tesseract
            import pytesseract
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                
                if text and conf > 0:
                    detections.append({
                        'text': text.upper(),
                        'confidence': conf / 100.0,
                        'box': None
                    })
        
        return detections
    
    def _extract_wagon_numbers(self, detections: List) -> Tuple[List[str], str, float]:
        """
        Extract wagon numbers from OCR detections
        
        Modes:
        - wagon: 11-digit wagon number rule (strict)
        - normal: All meaningful text (flexible)
        """
        wagon_numbers = []
        all_text_parts = []
        confidences = []
        
        if self.mode == 'wagon':
            # Wagon Mode: Strict 11-digit rule
            # Pattern: 2-4 letters + 7-9 digits = 11 total characters
            wagon_pattern = re.compile(r'[A-Z]{2,4}[-\s]?\d{7,9}')
        else:
            # Normal Mode: Any meaningful text (3+ characters)
            wagon_pattern = re.compile(r'[A-Z0-9]{3,}')
        
        for det in detections:
            text = det['text']
            conf = det['confidence']
            
            all_text_parts.append(text)
            confidences.append(conf)
            
            # Remove common noise words
            text_cleaned = text.replace('WAGON', '').replace('NO', '').strip()
            
            # Find wagon numbers in this text
            matches = wagon_pattern.findall(text_cleaned)
            
            for match in matches:
                # Clean up the match
                clean_match = match.replace(' ', '').replace('-', '')
                
                if self.mode == 'wagon':
                    # Wagon Mode: Strict validation
                    # Must be exactly 11 characters: 2-4 letters + 7-9 digits
                    has_letters = any(c.isalpha() for c in clean_match)
                    has_numbers = any(c.isdigit() for c in clean_match)
                    
                    if has_letters and has_numbers and len(clean_match) == 11:
                        if clean_match not in wagon_numbers:
                            wagon_numbers.append(clean_match)
                else:
                    # Normal Mode: Any meaningful text (3+ chars)
                    if len(clean_match) >= 3 and clean_match not in wagon_numbers:
                        wagon_numbers.append(clean_match)
        
        # Calculate overall confidence
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Combine all text
        all_text = ' '.join(all_text_parts)
        
        return wagon_numbers, all_text, avg_confidence
    
    def batch_process(self, input_folder: str, output_csv: str = None):
        """
        Process entire folder of images
        
        Args:
            input_folder: Folder with wagon images
            output_csv: Path to save results CSV
        """
        import pandas as pd
        from tqdm import tqdm
        
        # Find all images
        image_files = [f for f in os.listdir(input_folder)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"\n🔍 Processing {len(image_files)} images...")
        
        results_list = []
        
        for image_file in tqdm(image_files, desc="OCR Progress"):
            image_path = os.path.join(input_folder, image_file)
            
            try:
                result = self.process_image(image_path)
                
                results_list.append({
                    'filename': image_file,
                    'wagon_numbers': ', '.join(result['wagon_numbers']),
                    'num_detected': len(result['wagon_numbers']),
                    'all_text': result['all_text'],
                    'confidence': result['confidence'],
                    'status': 'success'
                })
                
            except Exception as e:
                results_list.append({
                    'filename': image_file,
                    'wagon_numbers': '',
                    'num_detected': 0,
                    'all_text': '',
                    'confidence': 0.0,
                    'status': f'error: {str(e)}'
                })
        
        # Create DataFrame
        df = pd.DataFrame(results_list)
        
        # Save to CSV
        if output_csv is None:
            output_csv = os.path.join(input_folder, 'ocr_results.csv')
        
        df.to_csv(output_csv, index=False)
        
        # Print summary
        print(f"\n{'='*60}")
        print("BATCH OCR SUMMARY")
        print(f"{'='*60}")
        print(f"Total images:        {len(image_files)}")
        print(f"Successful:          {len(df[df['status'] == 'success'])}")
        print(f"Errors:              {len(df[df['status'] != 'success'])}")
        print(f"Wagon numbers found: {df['num_detected'].sum()}")
        print(f"Avg confidence:      {df[df['status'] == 'success']['confidence'].mean():.2%}")
        print(f"\nResults saved to: {output_csv}")
        print(f"{'='*60}\n")
        
        return df


# =============================================================================
# QUICK START FUNCTIONS
# =============================================================================

def quick_single_image(image_path: str):
    """Extract wagon numbers from single image"""
    ocr = WagonNumberOCR(use_gpu=True)
    result = ocr.process_image(image_path, save_debug=True)
    
    print("\n" + "="*60)
    print(f"IMAGE: {image_path}")
    print("="*60)
    print(f"Wagon Numbers Found: {result['wagon_numbers']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"All Text: {result['all_text']}")
    print("="*60 + "\n")
    
    return result


def quick_batch(folder_path: str):
    """Extract wagon numbers from folder of images"""
    ocr = WagonNumberOCR(use_gpu=True)
    df = ocr.batch_process(folder_path)
    return df


# =============================================================================
# MAIN CLI
# =============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Wagon Number OCR with Deblurring')
    parser.add_argument('--image', type=str, help='Single image path')
    parser.add_argument('--folder', type=str, help='Folder with images')
    parser.add_argument('--output', type=str, help='Output CSV path')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU')
    
    args = parser.parse_args()
    
    if args.image:
        # Single image mode
        quick_single_image(args.image)
        
    elif args.folder:
        # Batch mode
        ocr = WagonNumberOCR(use_gpu=not args.no_gpu)
        ocr.batch_process(args.folder, args.output)
        
    else:
        # Interactive mode
        print("="*60)
        print("WAGON NUMBER OCR - Interactive Mode")
        print("="*60)
        print("\nChoose mode:")
        print("  1. Single image")
        print("  2. Batch folder")
        
        choice = input("\nEnter 1 or 2: ").strip()
        
        if choice == '1':
            img_path = input("Image path: ").strip()
            quick_single_image(img_path)
            
        elif choice == '2':
            folder = input("Folder path: ").strip()
            quick_batch(folder)
