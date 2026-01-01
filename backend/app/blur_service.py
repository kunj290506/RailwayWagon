import cv2
import os
import glob
import json
from typing import List
from app.models import FrameAnalysis

def calculate_blur_score(image_path: str) -> float:
    """
    Computes the Laplacian Variance of an image.
    Higher value = Sharper image.
    Lower value = Blurred image.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score

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
