import easyocr
import cv2
import logging
from typing import List
from app.models import OCRResult

import re

# Initialize EasyOCR reader
# gpu=True to attempt GPU usage. EasyOCR handles fallback to CPU if CUDA is missing, usually.
# We whitelist digits to improve accuracy for wagon numbers.
# Initialize EasyOCR reader
# gpu=True to attempt GPU usage. EasyOCR handles fallback to CPU if CUDA is missing, usually.
# We whitelist digits to improve accuracy for wagon numbers.
reader = easyocr.Reader(['en'], gpu=True)
import threading
ocr_lock = threading.Lock()

def run_ocr(image_path: str) -> List[OCRResult]:
    """
    Runs EasyOCR on the image.
    Returns list of detected texts and confidences.
    """
    try:
        with ocr_lock:
             # Manually load image to ensure stability and handle grayscale
             img = cv2.imread(image_path)
             if img is None:
                 print(f"Warning: Could not read image {image_path}")
                 return []

             # Convert to grayscale if it is color
             if len(img.shape) == 3:
                 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
             else:
                 gray = img
            
             # Pass the grayscale numpy array to EasyOCR
             results = reader.readtext(gray)
    except Exception as e:
        import traceback
        print(f"OCR Error processing {image_path}: {e}")
        traceback.print_exc()
        return []
    
    output = []
    # Result format: ([[x,y]...], text, confidence)
    for (bbox, text, prob) in results:
        output.append(OCRResult(
            text=text,
            confidence=round(prob, 2)
        ))
        
    return output

def extract_valid_wagon_numbers(ocr_results: List[OCRResult]) -> List[str]:
    """
    Filters OCR results for 11-digit sequences.
    """
    valid_numbers = []
    for res in ocr_results:
        # Remove spaces and non-alphanumeric (keep digits)
        clean_text = "".join(filter(str.isdigit, res.text))
        
        # Regex for 11 digit number
        # We search within the cleaned text
        matches = re.findall(r'\b\d{11}\b', clean_text)
        valid_numbers.extend(matches)
        
    return list(set(valid_numbers)) # Unique
