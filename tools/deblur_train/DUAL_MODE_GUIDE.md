# Dual-Mode OCR Usage Guide

## Two Modes Available

### 1. **WAGON MODE** (Default)
- **Rule**: Strict 11-digit wagon numbers only
- **Pattern**: 2-4 letters + 7-9 digits = 11 characters total
- **Examples**: 
  - `ABC12345678` ✅ (3 letters + 8 digits = 11)
  - `XY1234567890` ❌ (too long)
  - `ABCD123456` ❌ (only 10 characters)

### 2. **NORMAL MODE**
- **Rule**: Any meaningful text (3+ characters)
- **Pattern**: Detects all text, numbers, codes
- **Examples**:
  - `ABC` ✅
  - `123` ✅
  - `WAGON` ✅
  - `TEXT456` ✅

---

## Quick Usage

### CLI - Single Image
```bash
# Wagon mode (11-digit rule)
python wagon_ocr_pipeline.py --image test.jpg

# Normal mode (all text)
# Add mode parameter manually in code
```

### Python Code
```python
from wagon_ocr_pipeline import WagonNumberOCR

# WAGON MODE - Strict 11-digit rule
ocr_wagon = WagonNumberOCR(use_gpu=True, mode='wagon')
result = ocr_wagon.process_image('wagon.jpg')
print(result['wagon_numbers'])  # Only 11-digit wagon numbers

# NORMAL MODE - All meaningful text
ocr_normal = WagonNumberOCR(use_gpu=True, mode='normal')
result = ocr_normal.process_image('text.jpg')
print(result['wagon_numbers'])  # All text 3+ chars
```

### Test Both Modes
```bash
# Compare wagon vs normal mode
python test_dual_mode.py image.jpg --mode compare

# Test wagon mode only
python test_dual_mode.py image.jpg --mode wagon

# Test normal mode only
python test_dual_mode.py image.jpg --mode normal
```

---

## Mode Comparison Example

**Input Image Text**: `WAGON ABC12345678 RAIL XYZ456`

### Wagon Mode Output:
```
Detected: ['ABC12345678']
Reason: Only ABC12345678 matches 11-digit rule
```

### Normal Mode Output:
```
Detected: ['WAGON', 'ABC12345678', 'RAIL', 'XYZ456']
Reason: All text with 3+ characters
```

---

## Integration with MongoDB

```python
from wagon_ocr_pipeline import WagonNumberOCR
from wagon_ocr_mongodb import WagonOCRDatabase

# Choose mode
ocr = WagonNumberOCR(use_gpu=True, mode='wagon')  # or mode='normal'
db = WagonOCRDatabase()

# Process and save
result = ocr.process_image('image.jpg')
db.save_ocr_result({
    **result,
    'filename': 'image.jpg',
    'mode': ocr.mode  # Save which mode was used
})
```

---

## Use Cases

### Wagon Mode (11-digit)
- ✅ Railway wagon number detection
- ✅ Container tracking
- ✅ Strict format validation
- ✅ Database lookup (exact matches)

### Normal Mode (all text)
- ✅ General text extraction
- ✅ Reading labels, signs
- ✅ Document OCR
- ✅ Any text detection

---

## API Integration

### FastAPI Example with Mode Selection
```python
from fastapi import FastAPI, UploadFile, Form
from wagon_ocr_pipeline import WagonNumberOCR

app = FastAPI()

@app.post("/ocr")
async def ocr_image(
    file: UploadFile,
    mode: str = Form('wagon', enum=['wagon', 'normal'])
):
    # Save file
    image_path = f"uploads/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())
    
    # Process with selected mode
    ocr = WagonNumberOCR(use_gpu=True, mode=mode)
    result = ocr.process_image(image_path)
    
    return {
        "mode": mode,
        "detected": result['wagon_numbers'],
        "confidence": result['confidence']
    }
```

---

## Summary

| Feature | Wagon Mode | Normal Mode |
|---------|------------|-------------|
| **Pattern** | 11-digit strict | 3+ chars flexible |
| **Use Case** | Wagon numbers | General text |
| **Validation** | Very strict | Flexible |
| **Speed** | Same | Same |
| **Accuracy** | High (strict) | High (flexible) |

**Default**: Wagon Mode  
**Change**: Add `mode='normal'` parameter
