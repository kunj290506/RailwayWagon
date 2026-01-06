        raise HTTPException(status_code=404, detail="Batch not found")
    with open(path, "r") as f:
        return json.load(f)

# -------------------------------------------------------------------------
# BATCH IMAGE PROCESSING ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/batch_process")
async def batch_process_images(files: List[UploadFile] = File(...)):
    """
    Batch process multiple images:
    1. Deblur each image using AI model
    2. Run general OCR to extract ANY text
    3. Return enhanced images and OCR results
    """
    try:
        batch_input_dir = "data/batch_input"
        batch_enhanced_dir = "data/batch_enhanced"
       
        # Clear previous batch
        for dir_path in [batch_input_dir, batch_enhanced_dir]:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file))
        
        print(f"📁 Batch processing {len(files)} images...")
        
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
                
                enhance_image(input_path, enhanced_path)
                
                # Run general OCR (any text, not just numbers)
                ocr_results = run_ocr_general(enhanced_path)
                
                results.append({
                    "filename": file.filename,
                    "enhanced_filename": enhanced_filename,
                    "ocr_text": [{"text": r.text, "confidence": r.confidence} for r in ocr_results[:10]],  # Top 10 results
                    "status": "success"
                })
                
                print(f"  ✓ Processed {idx+1}/{len(files)}: {file.filename} ({len(ocr_results)} text items found)")
                
            except Exception as e:
                print(f"  ✗ Error processing {file.filename}: {e}")
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
    """Download all enhanced images as a ZIP file"""
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
