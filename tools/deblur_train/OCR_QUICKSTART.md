# Install OCR Dependencies

## BEST (Recommended): PaddleOCR
```bash
pip install paddleocr
pip install paddlepaddle-gpu  # If you have GPU
# OR
pip install paddlepaddle      # CPU only
```

## Good Alternative: EasyOCR
```bash
pip install easyocr
```

## Basic: Tesseract
```bash
pip install pytesseract
# Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

---

# Quick Start

## 1. Install OCR (choose one):
```bash
pip install paddleocr paddlepaddle-gpu
```

## 2. Single Image:
```bash
cd d:\adani\tools\deblur_train
python wagon_ocr_pipeline.py --image path/to/wagon.jpg
```

## 3. Batch Folder:
```bash
python wagon_ocr_pipeline.py --folder path/to/images --output results.csv
```

## 4. Python Usage:
```python
from wagon_ocr_pipeline import WagonNumberOCR

# Initialize
ocr = WagonNumberOCR(use_gpu=True)

# Process image
result = ocr.process_image('wagon.jpg')
print(result['wagon_numbers'])  # ['ABC123', 'XYZ789']

# Batch process
df = ocr.batch_process('images_folder', 'results.csv')
```

---

# Features

✅ **NAFNet Deblurring** - Pre-trained, instant sharp images  
✅ **Best OCR** - PaddleOCR (industrial-grade accuracy)  
✅ **Advanced Preprocessing** - Adaptive thresholding, denoising, sharpening  
✅ **Smart Extraction** - Regex pattern matching for wagon numbers  
✅ **Batch Processing** - Process folders with CSV output  
✅ **GPU Accelerated** - Fast processing  
✅ **Debug Mode** - Save intermediate images  

---

# Pipeline Flow

```
Input Image
    ↓
[NAFNet Deblurring]  ← Pre-trained, instant
    ↓
[Preprocessing]       ← Grayscale, threshold, denoise, sharpen
    ↓
[OCR Detection]       ← PaddleOCR/EasyOCR/Tesseract
    ↓
[Pattern Matching]    ← Extract wagon numbers (ABC123, XYZ789...)
    ↓
Result: Wagon Numbers + Confidence
```

---

# Accuracy Tips

1. **Use PaddleOCR** - Best accuracy for industrial text
2. **Enable GPU** - Much faster processing
3. **Good lighting** - Better input = better results
4. **Debug mode** - Check intermediate images if accuracy is low

---

# Example Output

```python
{
    'wagon_numbers': ['ABC123', 'XYZ789'],
    'all_text': 'WAGON ABC123 RAILWAY XYZ789',
    'confidence': 0.95,
    'deblurred_image': <numpy array>,
    'detections': [...]
}
```

CSV output:
```
filename,wagon_numbers,num_detected,all_text,confidence,status
img1.jpg,"ABC123, XYZ789",2,"WAGON ABC123...",0.95,success
img2.jpg,"DEF456",1,"DEF456",0.89,success
```
