# Add these imports at the top if not already present
from fastapi.responses import FileResponse
from typing import List
import zipfile

# Add this new endpoint after the existing ones (around line 525)

@app.post("/batch_process")
async def batch_process_images(files: List[UploadFile] = File(...)):
    """
    Batch process multiple images:
    1. Deblur each image
    2. Run OCR to extract ANY text (not limited to wagon numbers)
    3. Return enhanced images and OCR results
    """
    try:
        # Create batch directories
        batch_input_dir = "data/batch_input"
        batch_enhanced_dir = "data/batch_enhanced"
        os.makedirs(batch_input_dir, exist_ok=True)
        os.makedirs(batch_enhanced_dir, exist_ok=True)
        
        # Clear previous batch
        for dir_path in [batch_input_dir, batch_enhanced_dir]:
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))
        
        print(f"Processing {len(files)} images...")
        
        results = []
        
        for idx, file in enumerate(files):
            try:
                # Save input file
                input_path = os.path.join(batch_input_dir, file.filename)
                with open(input_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Deblur the image
                enhanced_filename = f"enhanced_{file.filename}"
                enhanced_path = os.path.join(batch_enhanced_dir, enhanced_filename)
                
                from backend.app.enhancement_service import enhance_image
                enhance_image(input_path, enhanced_path)
                
                # Run OCR on enhanced image (general text extraction)
                from backend.app.ocr_service import run_ocr_general
                ocr_results = run_ocr_general(enhanced_path)
                
                results.append({
                    "filename": file.filename,
                    "enhanced_filename": enhanced_filename,
                    "ocr_text": [{"text": r.text, "confidence": r.confidence} for r in ocr_results],
                    "status": "success"
                })
                
                print(f"Processed {idx+1}/{len(files)}: {file.filename}")
                
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "processed": len(files),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_batch_results")
async def download_batch_results():
    """
    Download all enhanced images as a ZIP file
    """
    try:
        batch_enhanced_dir = "data/batch_enhanced"
        zip_path = "data/batch_results.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(batch_enhanced_dir):
                file_path = os.path.join(batch_enhanced_dir, file)
                zipf.write(file_path, arcname=file)
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename='enhanced_images.zip'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
