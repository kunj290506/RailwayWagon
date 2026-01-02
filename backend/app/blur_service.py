import cv2
import os
import glob
import json
import numpy as np
from typing import List
from app.models import FrameAnalysis

def calculate_blur_score(image_path: str) -> float:
    """
    Computes the Laplacian Variance of an image.
    Higher value = Sharper image.
    Lower value = Blurred image.
    
    CRITICAL: This metric is sensitive to noise. A very noisy image might appear 'sharp'.
    Future TODO: Combine with Tenengrad gradient for robustness.
    """
    image = cv2.imread(image_path)
    if image is None:
        # Return 0 so it's classified as extremely blurry/invalid
        return 0.0
    
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Laplacian calculation
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return score
    except Exception:
        return 0.0

def analyze_frames(frames_dir: str, threshold: float = 100.0) -> List[FrameAnalysis]:
    """
    Analyzes all images in the directory for blur.
    Returns a sorted list of results (most blurred first).
    """
    results = []
    
    # Get all .jpg files
    frame_files = glob.glob(os.path.join(frames_dir, "*.jpg"))
    
    if not frame_files:
        return []

    for file_path in frame_files:
        filename = os.path.basename(file_path)
        try:
            score = calculate_blur_score(file_path)
            
            # Dynamic Thresholding?
            # For now, 100 is a standard heuristic for "focused" vs "blurry"
            state = "SHARP" if score > threshold else "BLURRED"
            
            results.append(FrameAnalysis(
                filename=filename,
                blur_score=round(score, 2),
                state=state
            ))
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")

    # Sort by blur score (ascending = most blurred first)
    results.sort(key=lambda x: x.blur_score)
    
    # Save to JSON
    output_path = "data/analysis.json"
    with open(output_path, "w") as f:
        json_data = [res.model_dump() for res in results]
        json.dump(json_data, f, indent=4)

    return results

def get_cached_results() -> List[FrameAnalysis]:
    try:
        with open("data/analysis.json", "r") as f:
            data = json.load(f)
            return [FrameAnalysis(**item) for item in data]
    except FileNotFoundError:
        return []
