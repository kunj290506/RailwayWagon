import cv2
import numpy as np
import os
import shutil
from typing import List
from app.models import FrameAnalysis

def enhance_image(image_path: str, output_path: str):
    """
    Applies Stronger CLAHE, Sharpening, and Saturation Boost to make enhancement obvious.
    """
    img = cv2.imread(image_path)
    if img is None:
        return

    # 1. Denoise first (to avoid sharpening noise)
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Stronger Clip Limit for more "HDR" look
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    limg = cv2.merge((cl, a, b))
    contrast_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # 3. Aggressive Sharpening
    # Laplacian Kernel for edges
    kernel = np.array([[-1, -1, -1], 
                       [-1,  9, -1], 
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(contrast_img, -1, kernel)
    
    # 4. Saturation Boost (to make it pop)
    hsv = cv2.cvtColor(sharpened, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.multiply(s, 1.2) # 20% more saturation
    s = np.clip(s, 0, 255).astype(np.uint8)
    hsv = cv2.merge((h, s, v))
    final_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    cv2.imwrite(output_path, final_img)

def enhance_frames(frames_dir: str, output_dir: str, blur_results: List[FrameAnalysis]) -> int:
    """
    Enhances frames based on their blur status.
    BLURRED -> Apply Enhancement.
    SHARP -> Copy original.
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    enhanced_count = 0

    # Map filename to result for easy lookup
    result_map = {res.filename: res for res in blur_results}
    
    # Iterate over actual files to be safe
    files = sorted(os.listdir(frames_dir))
    for filename in files:
        if filename not in result_map:
            continue
            
        analysis = result_map[filename]
        input_path = os.path.join(frames_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # We enforce enhancement on BLURRED frames
        # AND maybe even slightly on "SHARP" frames to make the video unified?
        # User said "Really it should be enhanced".
        # Let's trust the classification, but make the effect strong.
        
        if analysis.state == "BLURRED" or analysis.blur_score < 300: # Increase threshold for demo
            enhance_image(input_path, output_path)
            enhanced_count += 1
        else:
            # Copy original if it's already super sharp
            shutil.copy(input_path, output_path)
            
    return enhanced_count
