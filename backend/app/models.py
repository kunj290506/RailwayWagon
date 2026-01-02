from pydantic import BaseModel
from typing import List

class FrameAnalysis(BaseModel):
    filename: str
    blur_score: float
    state: str  # "SHARP" or "BLURRED"

class BlurResponse(BaseModel):
    total_frames: int
    results: List[FrameAnalysis]

class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: List[List[float]]  # 4 points [[x,y]...], in image pixel coords

class DetectionResult(BaseModel):
    label: str
    confidence: float
    box: List[float] # [x1, y1, x2, y2]

class AIComparisonResponse(BaseModel):
    filename: str
    original_ocr: List[OCRResult]
    enhanced_ocr: List[OCRResult]
    original_detections: List[DetectionResult]
    enhanced_detections: List[DetectionResult]
