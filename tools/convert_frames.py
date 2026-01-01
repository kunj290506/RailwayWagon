import cv2
import os
import glob
import sys
import re

def frames_to_video(input_dir, output_file, fps=30):
    print(f"Searching for images in {input_dir}...")
    
    # Try common extensions
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        images.extend(glob.glob(os.path.join(input_dir, ext)))
        # case insensitive check
        images.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    
    # Sort nicely (handle numbers: frame_1, frame_2, frame_10)
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]
    
    images.sort(key=natural_sort_key)
    
    if not images:
        print("No images found! Please check the path.")
        return

    print(f"Found {len(images)} images.")
    
    # Read first frame to get size
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    
    count = 0
    for img_path in images:
        frame = cv2.imread(img_path)
        if frame is None:
            continue
        
        # Resize if size changed (sanity check)
        if frame.shape[0] != height or frame.shape[1] != width:
            frame = cv2.resize(frame, (width, height))
            
        out.write(frame)
        count += 1
        if count % 50 == 0:
            print(f"Processed {count}/{len(images)}")

    out.release()
    print(f"Done! Video saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_frames.py <input_dir> <output_file>")
    else:
        frames_to_video(sys.argv[1], sys.argv[2])
