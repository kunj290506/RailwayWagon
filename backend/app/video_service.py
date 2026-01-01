import cv2
import os
import shutil

def process_video(file_path: str, output_dir: str, step: int = 5):
    """
    Reads a video file and extracts frames every 'step' frames.
    Saves frames to output_dir.
    Returns the count of saved frames.
    """
    # Clean output directory if it exists, or create it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(file_path)
    frame_count = 0
    saved_count = 0

    if not cap.isOpened():
        raise Exception(f"Could not open video file: {file_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract 1 frame every 'step' frames
        if frame_count % step == 0:
            frame_name = f"frame_{saved_count:04d}.jpg"
            frame_path = os.path.join(output_dir, frame_name)
            cv2.imwrite(frame_path, frame)
            saved_count += 1
        
        frame_count += 1

    cap.release()
    return saved_count

def create_video_from_frames(frames_dir: str, output_path: str, fps: float = 30.0):
    """
    Reassembles frames from a directory into an MP4 video.
    """
    frames = sorted([f for f in os.listdir(frames_dir) if f.endswith(('.jpg', '.png'))])
    if not frames:
        return False
        
    # Read first frame to get dimensions
    first_frame_path = os.path.join(frames_dir, frames[0])
    img = cv2.imread(first_frame_path)
    height, width, layers = img.shape
    
    # Define codec
    # 'mp4v' is widely supported for .mp4 containers on Windows/OpenCV
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        path = os.path.join(frames_dir, frame)
        img = cv2.imread(path)
        out.write(img)
        
    out.release()
    return True
