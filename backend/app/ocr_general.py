"""
General OCR service for any text (not limited to numbers)
"""

def run_ocr_general(image_path: str) -> List[OCRResult]:
    """
    Run OCR without filters - extract ANY text from image
    Better for general document/image text extraction
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
                # PaddleOCR - no restrictions
                ocr_results = ocr_engine.ocr(processed, cls=True)
                
                if ocr_results and ocr_results[0]:
                    for line in ocr_results[0]:
                        if line:
                            bbox, (text, confidence) = line
                            if confidence > 0.4:  # Minimum confidence
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
                    if prob > 0.4:
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
