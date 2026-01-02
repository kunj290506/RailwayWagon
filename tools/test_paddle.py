from paddleocr import PaddleOCR
import os
import sys

# Test on one frame
FRAME_PATH = r"d:\adani\data\batch_runs\output_video3\enhanced\frame_0200.jpg"

if not os.path.exists(FRAME_PATH):
    print(f"File not found: {FRAME_PATH}")
    sys.exit(1)

print(f"Testing PaddleOCR on {FRAME_PATH}...")
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=True)
    result = ocr.ocr(FRAME_PATH, cls=True)
    
    print("\n--- RESULTS ---")
    if result and result[0]:
        for line in result[0]:
            print(line)
    else:
        print("No text detected.")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
