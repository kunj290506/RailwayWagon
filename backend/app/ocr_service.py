import easyocr
import cv2
import logging
import numpy as np
import re
import threading
from typing import List
from app.models import OCRResult

# Initialize EasyOCR
# We trust EasyOCR more on this windows env than Paddle given the install issues.
try:
    reader = easyocr.Reader(['en'], gpu=True)
    print("✅ EasyOCR Initialized (GPU)")
except Exception as e:
    print(f"⚠️ EasyOCR GPU Init Failed: {e}. Falling back to CPU.")
    reader = easyocr.Reader(['en'], gpu=False)

ocr_lock = threading.Lock()

def preprocess_for_ocr(image):
    """
    Standard preprocessing for EasyOCR.
    Returns processed image and scale factors to map back to original.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Resize up if small
    h, w = gray.shape
    fx = fy = 1.0
    if h < 1000:
        fx = fy = 2.0
        gray = cv2.resize(gray, None, fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)

    # Contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    return enhanced, fx, fy

def run_ocr(image_path: str) -> List[OCRResult]:
    """
    Runs EasyOCR on the image.
    Returns list of detected texts and confidences.
    """
    try:
        # Load Image
        img = cv2.imread(image_path)
        if img is None:
            return []

        # Preprocess
        processed_img, fx, fy = preprocess_for_ocr(img)
        
        with ocr_lock:
             # EasyOCR readtext
             # allowlist='0123456789' forces digit-only mode
             results = reader.readtext(
                 processed_img, 
                 detail=1,
                 allowlist='0123456789', # Strict digit mode helps accuracy
                 paragraph=False,
                 min_size=10,
                 text_threshold=0.5,
                 low_text=0.3
             )
    except Exception as e:
        print(f"OCR Error: {e}")
        return []
    
    output = []
    # Result format: ([[x,y]...], text, confidence)
    for (bbox, text, prob) in results:
        # Lower threshold to 0.2 to catch faint numbers
        if prob > 0.2:
            # Map bbox back to original image coords (reverse of fx, fy)
            mapped = [[float(x)/fx, float(y)/fy] for (x, y) in bbox]
            output.append(OCRResult(
                text=text,
                confidence=round(prob, 2),
                bbox=mapped
            ))
        
    return output

def extract_valid_wagon_numbers(ocr_results: List[OCRResult]) -> List[dict]:
    """
    Filters OCR results for valid Wagon Numbers.
    Uses RELAXED Match Logic (8-15 digits).
    """
    valid_data = []
    
    # 1. Individual Blocks
    for res in ocr_results:
        clean_text = "".join(filter(str.isdigit, res.text))
        
        # Check if individual block looks like a number
        # 11 digits is ideal.
        if len(clean_text) >= 10 and len(clean_text) <= 12:
             valid_data.append({
                "number": clean_text,
                "confidence": res.confidence
            })

    # 2. Concatenated Frame Text (Fallback)
    full_text = " ".join([res.text for res in ocr_results])
    full_digits = "".join(filter(str.isdigit, full_text))
    
    # EXTREMELY RELAXED: Find 8 to 15 digits
    matches_full = re.finditer(r'\d{8,15}', full_digits)
    
    for m in matches_full:
        num = m.group()
        
        # Skip if already found exact match
        if any(d['number'] == num for d in valid_data):
            continue
            
        if len(num) == 11:
            valid_data.append({
                "number": num,
                "confidence": 0.85
            })
            print(f"[DEBUG OCR] Exact 11-Digit: {num}")
        else:
            # Partial
            valid_data.append({
                "number": num + " (?)", 
                "confidence": 0.45
            })
            print(f"[DEBUG OCR] Partial/Potential: {num}")

    # Deduplicate
    unique_map = {}
    for item in valid_data:
        num = item['number']
        # If duplicated, keep the one without (?) or higher confidence
        if num not in unique_map:
            unique_map[num] = item
        else:
             if '?' not in num and '?' in unique_map[num]['number']:
                 unique_map[num] = item
            
    return list(unique_map.values())

