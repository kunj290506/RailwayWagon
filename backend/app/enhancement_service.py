import cv2
import numpy as np
import os
import shutil
import time
import concurrent.futures
from typing import List
from app.models import FrameAnalysis

# Try Importing GPU Libraries
try:
    import torch
    import torch.nn.functional as F
    import kornia
    HAS_GPU_LIBS = True
except ImportError:
    HAS_GPU_LIBS = False
    print("⚠️ Kornia/Torch not found. Falling back to CPU OpenCV.")

def get_device():
    if HAS_GPU_LIBS and torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

# -----------------------------------------------------------------------------
# GPU PIPELINE (Fast, High Quality)
# -----------------------------------------------------------------------------
def enhance_image_gpu(image_path: str, output_path: str, device):
    try:
        # 1. Load to GPU (OpenCV Read -> Tensor)
        img_np = cv2.imread(image_path)
        if img_np is None: return
        
        # BGR -> RGB
        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        
        # To Tensor: (H, W, C) -> (1, C, H, W) normalized 0-1
        img_t = kornia.image_to_tensor(img_np, keepdim=False).float() / 255.0
        img_t = img_t.to(device)
        
        # 2. Glare Reduction (HSV Adjustments)
        # Convert to HSV
        img_hsv = kornia.color.rgb_to_hsv(img_t)
        
        # Split channels: (B, C, H, W)
        h, s, v = torch.chunk(img_hsv, chunks=3, dim=1)
        
        # Apply corrections (Vectorized on GPU)
        v = torch.clamp(v * 0.75, 0.0, 1.0) # Reduce brightness/glare
        s = torch.clamp(s * 1.15, 0.0, 1.0) # Boost saturation
        
        # Back to RGB
        img_hsv_fixed = torch.cat([h, s, v], dim=1)
        img_rgb = kornia.color.hsv_to_rgb(img_hsv_fixed)
        
        # 3. Contrast Enhancement (CLAHE on GPU!)
        # Kornia supports differentiable CLAHE
        # Note: Input must be Luminance or RGB. Kornia applies to L channel if passed RGB? 
        # Actually kornia.enhance.equalize_clahe expects (B, C, H, W).
        # We should apply it to Luminance for best results.
        img_lab = kornia.color.rgb_to_lab(img_rgb)
        l, a, b_chan = torch.chunk(img_lab, chunks=3, dim=1)
        
        # Apply CLAHE to L channel
        l_enhanced = kornia.enhance.equalize_clahe(l, clip_limit=2.2, grid_size=(8, 8))
        
        img_lab_enhanced = torch.cat([l_enhanced, a, b_chan], dim=1)
        img_contrast = kornia.color.lab_to_rgb(img_lab_enhanced)
        
        # 4. Sharpening (Unsharp Mask on GPU)
        # Kernel size (5,5), Sigma (1.5)
        img_sharp = kornia.filters.unsharp_mask(img_contrast, (5, 5), (1.5, 1.5))
        
        # 5. Upscale (Bilinear Interpolation on GPU)
        _, _, h_dim, w_dim = img_sharp.shape
        target_width = 2560
        
        if w_dim < target_width:
            scale_factor = target_width / w_dim
            new_h = int(h_dim * scale_factor)
            img_final = F.interpolate(img_sharp, size=(new_h, target_width), mode='bilinear', align_corners=False)
        else:
            img_final = img_sharp
            
        # 6. Save (Download from GPU)
        # Tensor (1, C, H, W) -> Numpy (H, W, C) BGR uint8
        img_out_rgb = kornia.tensor_to_image(img_final.byte() if False else (img_final * 255.0).byte())
        img_out_bgr = cv2.cvtColor(img_out_rgb, cv2.COLOR_RGB2BGR)
        
        cv2.imwrite(output_path, img_out_bgr)
        
    except Exception as e:
        print(f"GPU Enhancement Failed for {image_path}: {e}")
        # Fallback
        enhance_image_cpu(image_path, output_path)

# -----------------------------------------------------------------------------
# CPU FALLBACK (Original OpenCV Logic)
# -----------------------------------------------------------------------------
def enhance_image_cpu(image_path: str, output_path: str):
    img = cv2.imread(image_path)
    if img is None: return

    # 1. Reduce Sunlight / Glare
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v * 0.75, 0, 255).astype(np.uint8)
    s = np.clip(s * 1.15, 0, 255).astype(np.uint8)
    hsv_fixed = cv2.merge((h, s, v))
    glare_reduced = cv2.cvtColor(hsv_fixed, cv2.COLOR_HSV2BGR)

    # 2. CLAHE
    lab = cv2.cvtColor(glare_reduced, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab_enhanced = cv2.merge((l, a, b))
    contrast_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    # 3. Sharpen
    blur = cv2.GaussianBlur(contrast_enhanced, (0, 0), sigmaX=1.0)
    sharpened = cv2.addWeighted(contrast_enhanced, 1.5, blur, -0.5, 0)

    # 4. Upscale
    h_dim, w_dim = sharpened.shape[:2]
    target_width = 2560
    scale = target_width / w_dim
    if w_dim < target_width:
        final_img = cv2.resize(sharpened, (target_width, int(h_dim * scale)), interpolation=cv2.INTER_LINEAR)
    else:
        final_img = sharpened

    cv2.imwrite(output_path, final_img)

# -----------------------------------------------------------------------------
# DISPATCHER
# -----------------------------------------------------------------------------
def enhance_image(image_path: str, output_path: str):
    """
    Dispatches to GPU or CPU enhancement based on availability.
    """
    # FORCING CPU BACKEND TO FIX CUDA DSA ERRORS
    # device = get_device()
    # if device.type == 'cuda':
    #     enhance_image_gpu(image_path, output_path, device)
    # else:
    enhance_image_cpu(image_path, output_path)

# -----------------------------------------------------------------------------
# PARALLEL EXECUTION HANDLER
# -----------------------------------------------------------------------------
def process_single_frame(frames_dir, output_dir, filename, analysis):
    input_path = os.path.join(frames_dir, filename)
    output_path = os.path.join(output_dir, filename)
    
    # Logic: Enhance if BLURRED or low score
    if analysis.state == "BLURRED" or analysis.blur_score < 300: 
        enhance_image(input_path, output_path)
        return True # Enhanced
    else:
        shutil.copy(input_path, output_path)
        return False # Copied

def enhance_frames(frames_dir: str, output_dir: str, blur_results: List[FrameAnalysis], update_callback=None) -> int:
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    result_map = {res.filename: res for res in blur_results}
    files = sorted(os.listdir(frames_dir))
    valid_files = [f for f in files if f in result_map]
    total_files = len(valid_files)
    
    start_time = time.time()
    enhanced_count = 0
    processed_count = 0

    # THREADING MODEL:
    # - If CPU: High threads (IO bound/release GIL)
    # - If GPU: Low threads! 
    #   Why? Too many threads pushing to GPU causes Context Switch / OOM overhead. 
    #   Sequential GPU batching is best, but for simplicity here we use limit threads (e.g., 4).
    device = get_device()
    if device.type == 'cuda':
        # Don't overload the GPU queue or PCI-E bus
        max_workers = 4 
        print(f"🚀 Enhancing on {torch.cuda.get_device_name(0)} with {max_workers} workers.")
    else:
        max_workers = min(32, os.cpu_count() + 4)
        print("🐢 Enhancing on CPU.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_frame, frames_dir, output_dir, f, result_map[f]): f for f in valid_files}
        
        for future in concurrent.futures.as_completed(futures):
            is_enhanced = future.result()
            if is_enhanced: enhanced_count += 1
            
            processed_count += 1
            
            if update_callback and (processed_count % 5 == 0 or processed_count == total_files):
                elapsed = time.time() - start_time
                avg_time = elapsed / processed_count
                remaining = total_files - processed_count
                eta = avg_time * remaining
                progress = (processed_count / total_files) * 100
                update_callback(progress, eta)

    return enhanced_count
