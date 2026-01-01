import cv2
import numpy as np
import os
import shutil
from typing import List
from app.models import FrameAnalysis

def enhance_image(image_path: str, output_path: str):
    """
    Applies Advanced Enhancement: Glare Reduction -> CLAHE -> Bilateral Denoise -> Sharpening -> Upscale.
    """
    img = cv2.imread(image_path)
    if img is None:
        return

    # 1. Reduce Sunlight / Glare (HSV Space)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Reduce overexposed highlights
    v = np.clip(v * 0.75, 0, 255).astype(np.uint8)

    # Slight saturation boost (recovers faded paint/text)
    s = np.clip(s * 1.15, 0, 255).astype(np.uint8)

    hsv_fixed = cv2.merge((h, s, v))
    glare_reduced = cv2.cvtColor(hsv_fixed, cv2.COLOR_HSV2BGR)

    # 2. Local Contrast Enhancement (CLAHE)
    lab = cv2.cvtColor(glare_reduced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    l = clahe.apply(l)

    lab_enhanced = cv2.merge((l, a, b))
    contrast_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    # 3. Edge-Preserving Denoising
    denoised = cv2.bilateralFilter(
        contrast_enhanced,
        d=9,
        sigmaColor=75,
        sigmaSpace=75
    )

    # 4. Gentle Sharpening (OCR-safe)
    blur = cv2.GaussianBlur(denoised, (0, 0), sigmaX=0.8)
    sharpened = cv2.addWeighted(denoised, 1.25, blur, -0.25, 0)

    # 5. Upscale to True 2K (Lanczos – best quality)
    h_dim, w_dim = sharpened.shape[:2]
    target_width = 2560
    scale = target_width / w_dim
    
    # Only upscale if smaller
    if w_dim < target_width:
        final_img = cv2.resize(
            sharpened,
            (target_width, int(h_dim * scale)),
            interpolation=cv2.INTER_LANCZOS4
        )
    else:
        final_img = sharpened

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
