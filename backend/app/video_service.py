import cv2
import os
import shutil

def process_video(file_path: str, output_dir: str, step: int = 10, max_frames: int = 100):
    """
    OPTIMIZED: Fast frame extraction
    - Extracts every 'step' frames (default 10 for speed)
    - Limits total frames to max_frames
    - Uses faster JPEG quality settings
    - Skips frames efficiently with cap.set()
    """
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video file: {file_path}")
    
    # Get total frames and FPS
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate actual step to stay under max_frames
    if total_frames // step > max_frames:
        step = max(total_frames // max_frames, 1)
    
    saved_count = 0
    frame_idx = 0
    
    # Faster JPEG compression (lower quality for speed)
    jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, 85]  # Was 95, now 85 (faster)
    
    while frame_idx < total_frames and saved_count < max_frames:
        # Seek directly to frame (faster than reading all frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Resize frame to 720p max for speed (maintains aspect ratio)
        h, w = frame.shape[:2]
        if max(h, w) > 720:
            scale = 720 / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        frame_name = f"frame_{saved_count:04d}.jpg"
        frame_path = os.path.join(output_dir, frame_name)
        cv2.imwrite(frame_path, frame, jpeg_params)
        
        saved_count += 1
        frame_idx += step
    
    cap.release()
    print(f"⚡ Fast extraction: {saved_count} frames from {total_frames} (step={step})")
    return saved_count


def create_video_from_frames(frames_dir: str, output_path: str, fps: float = 10.0):
    """
    OPTIMIZED: Fast video creation
    - Lower FPS (10 instead of 30) for smaller files
    - H.264 codec for better compression
    """
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(('.jpg', '.png'))])
    if not frames:
        return False
    
    first_frame_path = os.path.join(frames_dir, frames[0])
    img = cv2.imread(first_frame_path)
    height, width = img.shape[:2]
    
    # Try H.264 first (better compression), fallback to mp4v
    try:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264
    except:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        path = os.path.join(frames_dir, frame)
        img = cv2.imread(path)
        out.write(img)
    
    out.release()
    print(f"⚡ Created video: {len(frames)} frames @ {fps} FPS")
    return True
