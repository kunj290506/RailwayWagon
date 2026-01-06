# MongoDB Integration for Wagon OCR

## Quick Setup

### 1. Install MongoDB
```bash
# Windows: Download from https://www.mongodb.com/try/download/community
# OR use Docker:
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Install Python Package
```bash
pip install pymongo
```

### 3. Start Using
```bash
cd d:\adani\tools\deblur_train

# Process single image
python ocr_with_mongodb.py --image path/to/wagon.jpg

# Process folder
python ocr_with_mongodb.py --folder path/to/images

# View statistics
python wagon_ocr_mongodb.py --stats

# Search for wagon number
python wagon_ocr_mongodb.py --search ABC123
```

---

## Features

✅ **Automatic Storage** - OCR results saved to MongoDB automatically  
✅ **Fast Queries** - Search by wagon number, filename, or date  
✅ **Statistics** - Track detection rates and confidence scores  
✅ **Deduplication** - Unique wagon numbers with occurrence count  
✅ **CSV Import/Export** - Migrate existing data  
✅ **Indexed** - Optimized for fast lookups  

---

## MongoDB Collections

### `ocr_results`
Stores every processed image:
```javascript
{
  filename: "wagon123.jpg",
  wagon_numbers: ["ABC123", "XYZ789"],
  all_text: "WAGON ABC123 RAILWAY XYZ789",
  confidence: 0.95,
  num_detected: 2,
  timestamp: ISODate("2026-01-06T16:30:00Z"),
  status: "success",
  metadata: {
    image_path: "/path/to/wagon123.jpg",
    processing_time: 1.5,
    ocr_engine: "paddle"
  }
}
```

### `wagon_numbers`
Unique wagon numbers with statistics:
```javascript
{
  number: "ABC123",
  count: 15,  // Seen in 15 images
  first_seen: ISODate("2026-01-01T10:00:00Z"),
  last_seen: ISODate("2026-01-06T16:30:00Z"),
  last_filename: "wagon123.jpg"
}
```

---

## Python Usage

### Basic Usage
```python
from wagon_ocr_pipeline import WagonNumberOCR
from wagon_ocr_mongodb import WagonOCRDatabase, process_and_save_to_db

# Initialize
ocr = WagonNumberOCR(use_gpu=True)
db = WagonOCRDatabase()  # Uses localhost by default

# Process and save
process_and_save_to_db('wagon.jpg', db, ocr)
```

### Query Database
```python
# Search for wagon number
results = db.search_by_wagon_number('ABC123')
for r in results:
    print(f"Found in {r['filename']} on {r['timestamp']}")

# Get recent results
recent = db.get_recent_results(limit=10)

# Get statistics
stats = db.get_statistics()
print(f"Total processed: {stats['total_images']}")
print(f"Unique wagons: {stats['unique_wagon_numbers']}")
```

### Batch Processing
```python
# Process folder and save to MongoDB
from ocr_with_mongodb import process_with_mongodb

process_with_mongodb(folder_path='images/')
```

---

## Commands

### Setup Database
```bash
python wagon_ocr_mongodb.py --setup
```

### Process Images
```bash
# Single
python ocr_with_mongodb.py --image wagon.jpg

# Batch
python ocr_with_mongodb.py --folder images/
```

### View Statistics
```bash
python wagon_ocr_mongodb.py --stats
```

**Output:**
```
DATABASE STATISTICS
================
Total images processed:    1542
Successful detections:     1489
Failed detections:         53
Unique wagon numbers:      987
Average confidence:        93.2%
```

### Search
```bash
# Find all images with wagon number
python wagon_ocr_mongodb.py --search ABC123

# Show recent results
python wagon_ocr_mongodb.py --recent 20
```

### Import/Export
```bash
# Import existing CSV
python wagon_ocr_mongodb.py --import-csv results.csv

# Export to CSV
python wagon_ocr_mongodb.py --export-csv backup.csv
```

---

## Connection String

### Local MongoDB
```python
db = WagonOCRDatabase()  # Default: mongodb://localhost:27017/
```

### Remote MongoDB
```python
db = WagonOCRDatabase(connection_string='mongodb://user:pass@host:27017/')
```

### MongoDB Atlas (Cloud)
```python
uri = 'mongodb+srv://user:pass@cluster.mongodb.net/'
db = WagonOCRDatabase(connection_string=uri)
```

### Environment Variable
```bash
export MONGODB_URI='mongodb://localhost:27017/'
python ocr_with_mongodb.py --image wagon.jpg
```

---

## Integration with Your App

### FastAPI Example
```python
from fastapi import FastAPI, UploadFile
from wagon_ocr_pipeline import WagonNumberOCR
from wagon_ocr_mongodb import WagonOCRDatabase

app = FastAPI()
ocr = WagonNumberOCR(use_gpu=True)
db = WagonOCRDatabase()

@app.post("/ocr/wagon")
async def upload_wagon_image(file: UploadFile):
    # Save file
    image_path = f"uploads/{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())
    
    # Process and save to MongoDB
    result = ocr.process_image(image_path)
    doc_id = db.save_ocr_result({
        **result,
        'filename': file.filename,
        'image_path': image_path
    })
    
    return {
        "wagon_numbers": result['wagon_numbers'],
        "confidence": result['confidence'],
        "document_id": doc_id
    }

@app.get("/search/{wagon_number}")
async def search_wagon(wagon_number: str):
    results = db.search_by_wagon_number(wagon_number)
    return {"results": results}
```

---

## Files Created

| File | Purpose |
|------|---------|
| `wagon_ocr_mongodb.py` | MongoDB database layer |
| `ocr_with_mongodb.py` | Unified OCR + MongoDB script |

---

## Summary

✅ MongoDB integration complete  
✅ Automatic result storage  
✅ Fast search and queries  
✅ Statistics tracking  
✅ CSV import/export  
✅ Ready for production use  

Start using:
```bash
python ocr_with_mongodb.py --folder your_images/
```
