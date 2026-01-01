import cv2
import numpy as np
import random
import os

def create_synthetic_video(output_path="sample_video.mp4", duration_sec=5, fps=30):
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Fonts
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Simulation params
    num_frames = duration_sec * fps
    wagon_color = (40, 40, 40) # Dark gray
    
    print(f"Generating video: {output_path} ({num_frames} frames)")

    for i in range(num_frames):
        # Background (Night time - dark blue/black)
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (20, 10, 10) # Dark background

        # Simulate Wagon Movement (Moving Right to Left)
        speed = 20 # pixels per frame
        # We'll have multiple wagons passing by
        wagon_width = 800
        wagon_gap = 200
        total_cycle = wagon_width + wagon_gap
        
        # Calculate position based on time
        offset = (i * speed) % total_cycle
        
        # Draw Wagon (simple rectangle)
        start_x = width - offset
        
        # If wagon is visible
        if start_x < width:
            # Wagon body
            cv2.rectangle(img, (int(start_x), 200), (int(start_x + wagon_width), 600), wagon_color, -1)
            # Wagon border
            cv2.rectangle(img, (int(start_x), 200), (int(start_x + wagon_width), 600), (100,100,100), 2)
            
            # Wagon Number (The OCR target)
            text = "WAGON-7392"
            text_size = cv2.getTextSize(text, font, 2, 3)[0]
            text_x = int(start_x + (wagon_width - text_size[0]) / 2)
            text_y = 400
            
            # Draw Text
            cv2.putText(img, text, (text_x, text_y), font, 2, (200, 200, 200), 3, cv2.LINE_AA)
            
            # Add some rusty details/noise
            noise = np.random.randint(0, 50, (400, wagon_width, 3), dtype=np.uint8)
            # overlay noise? (Keep it simple for now)

        # ------------------------------------------------
        # SIMULATE DEFECTS (Motion Blur + Low Light)
        # ------------------------------------------------
        
        # Vary blur intensity over time (Sin wave)
        # Some frames sharp, some very blurry
        blur_factor = (np.sin(i / 10.0) + 1) / 2 # 0 to 1
        
        # If blur_factor high -> High Speed/Blur
        kernel_size = int(1 + 20 * blur_factor) 
        if kernel_size % 2 == 0: kernel_size += 1
        
        # Motion Blur Kernel (Horizontal)
        kernel = np.zeros((kernel_size, kernel_size))
        kernel[int((kernel_size-1)/2), :] = np.ones(kernel_size)
        kernel /= kernel_size
        
        # Apply blur
        img = cv2.filter2D(img, -1, kernel)
        
        # Add Low Light Noise
        noise_level = 20
        noise = np.random.normal(0, noise_level, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)

        # Make it darker (Night mode)
        img = (img * 0.7).astype(np.uint8)

        out.write(img)

    out.release()
    print("Video generation complete.")

if __name__ == "__main__":
    if not os.path.exists("data"):
        os.makedirs("data")
    create_synthetic_video("data/sample_video.mp4")
