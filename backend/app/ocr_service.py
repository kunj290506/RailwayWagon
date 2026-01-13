import cv2
import numpy as np
import logging
import re
import threading
from typing import List
from backend.app.models import OCRResult

# Try PaddleOCR first (better for Asian/numeric text), fallback to EasyOCR
ocr_engine = None
ocr_lock = threading.Lock()

try:
    from paddleocr import PaddleOCR
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True, show_log=False)
    print("✅ PaddleOCR Initialized (GPU) - Superior number detection")
except Exception as e:
    print(f"⚠️ PaddleOCR unavailable: {e}. Using EasyOCR...")
    try:
        import easyocr
        ocr_engine = easyocr.Reader(['en'], gpu=True)
        print("✅ EasyOCR Initialized (GPU)")
    except Exception as e2:
        print(f"❌ Both OCR engines failed: {e2}")
        import easyocr
        ocr_engine = easyocr.Reader(['en'], gpu=False)
        print("⚠️ EasyOCR CPU Mode")

def advanced_preprocess(image):
    """
    Enhanced preprocessing for better wagon number detection
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Resize for better OCR (larger = better detection)
    h, w = gray.shape
    if h < 1200:
        scale = 2.0  # Increased from 2.5
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Enhance contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Adaptive thresholding
    binary = cv2.adaptiveThreshold(
        sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return morph

def run_ocr(image_path: str) -> List[OCRResult]:
    """
    Enhanced OCR with PaddleOCR/EasyOCR
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Try multiple preprocessing strategies
        results = []
        
        # Strategy 1: Advanced preprocessing
        processed = advanced_preprocess(img)
        
        with ocr_lock:
            if 'PaddleOCR' in str(type(ocr_engine)):
                # PaddleOCR
                ocr_results = ocr_engine.ocr(processed, cls=True)
                
                if ocr_results and ocr_results[0]:
                    for line in ocr_results[0]:
                        if line:
                            bbox, (text, confidence) = line
                            # Only digits
                            clean_text = ''.join(filter(str.isdigit, text))
                            if len(clean_text) >= 4 and confidence > 0.3:
                                results.append(OCRResult(
                                    text=clean_text,
                                    confidence=round(confidence, 2),
                                    bbox=bbox
                                ))
            else:
                # EasyOCR
                ocr_results = ocr_engine.readtext(
                    processed,
                    detail=1,
                    allowlist='0123456789',
                    paragraph=False,
                    min_size=10,
                    text_threshold=0.4,
                    low_text=0.2
                )
                
                for (bbox, text, prob) in ocr_results:
                    if prob > 0.3:
                        clean_text = ''.join(filter(str.isdigit, text))
                        if len(clean_text) >= 4:
                            results.append(OCRResult(
                                text=clean_text,
                                confidence=round(prob, 2),
                                bbox=bbox
                            ))
        
        # Strategy 2: Original image (sometimes works better)
        if len(results) < 2:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            with ocr_lock:
                if 'PaddleOCR' in str(type(ocr_engine)):
                    extra_results = ocr_engine.ocr(gray, cls=True)
                    if extra_results and extra_results[0]:
                        for line in extra_results[0]:
                            if line:
                                bbox, (text, confidence) = line
                                clean_text = ''.join(filter(str.isdigit, text))
                                if len(clean_text) >= 4 and confidence > 0.3:
                                    # Check not duplicate
                                    if not any(r.text == clean_text for r in results):
                                        results.append(OCRResult(
                                            text=clean_text,
                                            confidence=round(confidence, 2),
                                            bbox=bbox
                                        ))
        
        return results
        
    except Exception as e:
        print(f"OCR Error on {image_path}: {e}")
        return []

def extract_valid_wagon_numbers(ocr_results: List[OCRResult]) -> List[dict]:
    """
    Improved wagon number extraction with better validation
    Supports both numeric-only and alphanumeric patterns
    """
    valid_data = []
    
    # Collect all detected text
    all_texts = [res.text for res in ocr_results]
    
    # Strategy 1: Look for 10-12 digit sequences (numeric wagon numbers)
    for res in ocr_results:
        clean = res.text.strip()
        
        # Pure numeric 10-12 digits
        if clean.isdigit() and 10 <= len(clean) <= 12:
            valid_data.append({
                "number": clean,
                "confidence": res.confidence
            })
    
    # Strategy 2: Look for alphanumeric patterns (letters + numbers)
    # Pattern: 2-4 letters followed by 7-9 digits
    import re
    for text in all_texts:
        # Match patterns like ABC1234567 or XY12345678
        matches = re.findall(r'[A-Z]{2,4}\s?-?\s?\d{7,9}', text.upper())
        for match in matches:
            clean = re.sub(r'[\s-]', '', match)  # Remove spaces and dashes
            if clean not in [d['number'] for d in valid_data]:
                valid_data.append({
                    "number": clean,
                    "confidence": 0.75
                })
    
    # Strategy 3: Concatenate nearby results to find split numbers
    concat_text = ''.join([res.text for res in ocr_results])
    
    # Find 10-14 digit sequences in concatenated text
    for match in re.finditer(r'\d{10,14}', concat_text):
        num = match.group()
        
        # Skip if already found
        if any(d['number'] == num for d in valid_data):
            continue
        
        # Prefer 11-digit (standard wagon number)
        if len(num) == 11:
            valid_data.append({
                "number": num,
                "confidence": 0.70
            })
    
    # Deduplicate and sort by confidence
    unique_map = {}
    for item in valid_data:
        num = item['number']
        if num not in unique_map or item['confidence'] > unique_map[num]['confidence']:
            unique_map[num] = item
    
    sorted_results = sorted(unique_map.values(), key=lambda x: x['confidence'], reverse=True)
    
    return sorted_results


def run_ocr_general(image_path: str) -> List[OCRResult]:
    """
    Run OCR without filters - extract ANY text from image
    For general document/image text extraction (not just wagon numbers)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Use same advanced preprocessing
        processed = advanced_preprocess(img)
        
        results = []
        
        with ocr_lock:
            if 'PaddleOCR' in str(type(ocr_engine)):
                # PaddleOCR - no character restrictions
                ocr_results = ocr_engine.ocr(processed, cls=True)
                
                if ocr_results and ocr_results[0]:
                    for line in ocr_results[0]:
                        if line:
                            bbox, (text, confidence) = line
                            if confidence > 0.4 and text.strip():
                                results.append(OCRResult(
                                    text=text.strip(),
                                    confidence=round(confidence, 2),
                                    bbox=bbox
                                ))
            else:
                # EasyOCR - no character restrictions
                ocr_results = ocr_engine.readtext(
                    processed,
                    detail=1,
                    paragraph=False,
                    min_size=10,
                    text_threshold=0.5
                )
                
                for (bbox, text, prob) in ocr_results:
                    if prob > 0.4 and text.strip():
                        results.append(OCRResult(
                            text=text.strip(),
                            confidence=round(prob, 2),
                            bbox=bbox
                        ))
        
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        return results
        
    except Exception as e:
        print(f"General OCR Error on {image_path}: {e}")
        return []
