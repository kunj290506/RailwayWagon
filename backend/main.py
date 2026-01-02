from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import json
from app.video_service import process_video
from app.blur_service import analyze_frames
from app.enhancement_service import enhance_frames
from app.ocr_service import run_ocr
from app.detection_service import run_detection
from app.models import BlurResponse, AIComparisonResponse

app = FastAPI()
        
# Helper for Cleanup
def cleanup_session_data():
    print("🧹 Cleaning up live session data...")
    # Directories to clear
    dirs_to_clear = ["data/frames", "data/enhanced", "data/uploads"]
    for d in dirs_to_clear:
        if os.path.exists(d):
            # Remove all contents but keep directory
            for filename in os.listdir(d):
                file_path = os.path.join(d, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")

    # Files to remove
    files_to_remove = ["data/wagons.json", "data/metadata.json", "data/analysis.json", "data/original_video.mp4", "data/enhanced_video.mp4"]
    for f in files_to_remove:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception as e:
                 print(f"Failed to delete {f}. Reason: {e}")
    
    # Reset status
    global server_status
    server_status = { "step": "Idle", "message": "Ready", "progress": 0 }

@app.on_event("startup")
async def startup_event():
    import torch
    print("------------------------------------------------")
    print("      AI Engine Startup Checks")
    print("------------------------------------------------")
    try:
        if torch.cuda.is_available():
            print(f"✅ GPU Detected: {torch.cuda.get_device_name(0)}")
            print("   PyTorch is using CUDA.")
        else:
            print("⚠️  No GPU via PyTorch. Using CPU.")
    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        
    cleanup_session_data()

    print("------------------------------------------------")

# Allow frontend running on Vite's default port
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure data directories exist
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/frames", exist_ok=True)
os.makedirs("data/enhanced", exist_ok=True)

# Mount static files to serve frames later
app.mount("/static/frames", StaticFiles(directory="data/frames"), name="static_frames")
app.mount("/static/enhanced", StaticFiles(directory="data/enhanced"), name="static_enhanced")
# Mount the data root so we can serve the generated mp4s
app.mount("/static/data", StaticFiles(directory="data"), name="static_data")

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.post("/reset_session")
def reset_session_endpoint():
    try:
        cleanup_session_data()
        return {"message": "Session Reset Complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    try:
        # 1. CLEANUP LIVE SESSION DATA (User Requested "Fresh Start" per upload)
        # We assume every new video upload implies a new inspection session.
        print(f"🧹 Purging previous session data for new upload: {file.filename}")
        cleanup_session_data()

        # 2. Save uploaded file
        file_location = f"data/uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Process video (extract frames)
        output_dir = "data/frames"
        # Increase step to 15 for MUCH faster processing (approx 2 fps extracted)
        num_frames = process_video(file_location, output_dir, step=15)
        
        return {
            "message": "Video processed successfully (Previous session cleared)",
            "filename": file.filename,
            "frames_extracted": num_frames
        }
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_blur", response_model=BlurResponse)
def analyze_blur():
    try:
        frames_dir = "data/frames"
        enhanced_dir = "data/enhanced"
        results = analyze_frames(frames_dir, threshold=100.0)

        # Auto-populate enhanced images so Frame Comparison can display immediately
        try:
            need_enhance = (not os.path.exists(enhanced_dir)) or (len(os.listdir(enhanced_dir)) == 0)
            if need_enhance and results:
                enhance_frames(frames_dir, enhanced_dir, results)
        except Exception as _e:
            # Non-fatal: still return analysis results even if enhancement fails
            print(f"Auto-enhance skipped: {_e}")
        return {
            "total_frames": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enhance_frames")
def enhance_frames_endpoint():
    try:
        update_status("Enhancement", "Initializing Pipeline...", 0)
        
        frames_dir = "data/frames"
        enhanced_dir = "data/enhanced"
        
        # We need the blur results to decided which to enhance
        blur_results = analyze_frames(frames_dir, threshold=100.0)
        
        # Callback for ETA
        def status_update(prog, eta):
            eta_val = int(eta)
            eta_str = f"{eta_val // 60}m {eta_val % 60}s" if eta_val > 60 else f"{eta_val}s"
            # Update global status
            update_status("Enhancement", f"Enhancing... Remaining: {eta_str}", int(prog))
            server_status["eta"] = eta_str

        count = enhance_frames(frames_dir, enhanced_dir, blur_results, update_callback=status_update)
        
        # NEW: Reassemble Enhanced Video for the Player
        update_status("Enhancement", "Reassembling Video...", 95)
        server_status["eta"] = "~10s"
        
        from app.video_service import create_video_from_frames
        # We assume 30 FPS for the output primarily
        create_video_from_frames(enhanced_dir, "data/enhanced_video.mp4", fps=30.0)
        
        # Also ensure we have an original video in a standard place (copy upload)
        create_video_from_frames(frames_dir, "data/original_video.mp4", fps=30.0)
        
        update_status("Enhancement", "Complete", 100)
        server_status["eta"] = "0s"
        
        return {"message": "Enhancement and Reassembly complete", "enhanced_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_ocr", response_model=AIComparisonResponse)
def run_ocr_endpoint(filename: str):
    original_path = f"data/frames/{filename}"
    enhanced_path = f"data/enhanced/{filename}"
    
    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Original frame not found")
    
    # If enhanced doesn't exist (maybe it was sharp enough), allow fallback to original or specific logic
    # For this MVP, we assume enhanced folder is populated. If file missing there, means it wasn't enhanced (sharp).
    # We can use original for "enhanced" metric if it wasn't processed, OR just skip.
    # Let's try to verify if it exists.
    target_enhanced_path = enhanced_path if os.path.exists(enhanced_path) else original_path

    try:
        res_orig = run_ocr(original_path)
        res_enh = run_ocr(target_enhanced_path)
        
        return AIComparisonResponse(
            filename=filename,
            original_ocr=res_orig,
            enhanced_ocr=res_enh,
            original_detections=[],
            enhanced_detections=[]
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_detection", response_model=AIComparisonResponse)
def run_detection_endpoint(filename: str):
    original_path = f"data/frames/{filename}"
    enhanced_path = f"data/enhanced/{filename}"
    
    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Original frame not found")
        
    target_enhanced_path = enhanced_path if os.path.exists(enhanced_path) else original_path

    try:
        res_orig = run_detection(original_path)
        res_enh = run_detection(target_enhanced_path)
        
        return AIComparisonResponse(
            filename=filename,
            original_ocr=[],
            enhanced_ocr=[],
            original_detections=res_orig,
            enhanced_detections=res_enh
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/top_blur")
def get_top_blur(limit: int = 10):
    from app.blur_service import get_cached_results
    results = get_cached_results()
    return results[:limit]

@app.get("/analytics/metrics")
def get_metrics():
    from app.blur_service import get_cached_results
    results = get_cached_results()
    
    total = len(results)
    if total == 0:
        return {"total": 0, "blurred_count": 0, "blurred_percentage": 0}
        
    blurred_count = sum(1 for r in results if r.state == "BLURRED")
    
    return {
        "total": total,
        "blurred_count": blurred_count,
        "blurred_percentage": round((blurred_count / total) * 100, 1)
    }

# Global Status for Polling
server_status = {
    "step": "Idle",
    "message": "Ready",
    "progress": 0
}

@app.get("/status")
def get_status():
    return server_status

def update_status(step, message, progress):
    global server_status
    server_status["step"] = step
    server_status["message"] = message
    server_status["progress"] = progress

@app.post("/scan_wagons")
def scan_wagons():
    """
    Runs OCR on all ENHANCED frames to find unique 11-digit wagon numbers.
    ARCHIVES results for history.
    """
    from app.ocr_service import run_ocr, extract_valid_wagon_numbers
    from datetime import datetime
    
    update_status("Scanning", "Initializing Wagon Scanner...", 0)
    
    enhanced_dir = "data/enhanced"
    frames_dir = "data/frames"
    
    if not os.path.exists(enhanced_dir):
        update_status("Idle", "Scan Complete (No frames)", 100)
        return {"wagons": []}
    
    frames = sorted(os.listdir(enhanced_dir))
    frames_to_scan = frames[::5] # Optimize
    total_scan = len(frames_to_scan)
    
    found_wagons = {} # number -> first_seen_frame
    
    print(f"Scanning {total_scan} frames out of {len(frames)} total...")
    
    import time
    start_time = time.time()

    for i, frame in enumerate(frames_to_scan):
        # ETA Calculation
        processed = i + 1
        elapsed = time.time() - start_time
        avg_time = elapsed / processed
        remaining = total_scan - processed
        eta_val = int(avg_time * remaining)
        eta_str = f"{eta_val // 60}m {eta_val % 60}s" if eta_val > 60 else f"{eta_val}s"

        update_status("Scanning", f"Scanning {i+1}/{total_scan} - Rem: {eta_str}", int((i / total_scan) * 100))
        server_status["eta"] = eta_str
        
        if not (frame.endswith(".jpg") or frame.endswith(".png")):
            continue
            
        path = os.path.join(enhanced_dir, frame)
        ocr_results = run_ocr(path)
        
        # New: Returns list of dicts {'number': str, 'confidence': float}
        wagon_objects = extract_valid_wagon_numbers(ocr_results)
        
        for w_obj in wagon_objects:
            num = w_obj['number']
            conf = w_obj['confidence']
            
            # Logic: If new, add. If existing, update ONLY if confidence is better?
            # For now, let's just keep the first one found or maybe the one with best confidence?
            # Let's simple keep first found to map it to the earliest frame (good for timeline).
            # But we want to record the MAX confidence observed across frames.
            
            if num not in found_wagons:
                found_wagons[num] = {
                    "frame": frame,
                    "confidence": conf,
                    "first_seen": frame
                }
                print(f"Found Wagon: {num} (Conf: {conf}) in {frame}")
            else:
                # Update max confidence if this sighting is better
                if conf > found_wagons[num]["confidence"]:
                    found_wagons[num]["confidence"] = conf
                    # We keep "frame" as the best confidence frame? 
                    # Yes, show the clearest image.
                    found_wagons[num]["frame"] = frame 

    # Format result
    result_list = []
    for num, data in found_wagons.items():
        result_list.append({
            "number": num,
            "frame": data["frame"],
            "confidence": data["confidence"], # Pass to frontend
            "image_url": f"http://localhost:8000/static/enhanced/{data['frame']}"
        })
    
    # Save current session
    with open("data/wagons.json", "w") as f:
        json.dump(result_list, f, indent=4)

    # GENERATE MASTER METADATA
    master_meta = []
    from app.blur_service import get_cached_results
    blur_data = get_cached_results()
    blur_data.sort(key=lambda x: x.filename)
    
    wagon_map = {w['frame']: w['number'] for w in result_list}
    
    for idx, b in enumerate(blur_data):
        master_meta.append({
            "frame_index": idx,
            "filename": b.filename,
            "timestamp": idx / 30.0,
            "blur_score": b.blur_score,
            "is_blurred": b.state == "BLURRED",
            "wagon_number": wagon_map.get(b.filename, None)
        })
        
    with open("data/metadata.json", "w") as f:
        json.dump(master_meta, f)

    # -------------------------------------------------------------------------
    # ARCHIVING LOGIC
    # -------------------------------------------------------------------------
    try:
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_root = f"data/history/{batch_id}"
        archive_img_root = f"{history_root}/images"
        os.makedirs(archive_img_root, exist_ok=True)
        
        # 1. Archive Wagon Frames (Enhanced)
        for w in result_list:
             src = os.path.join(enhanced_dir, w['frame'])
             dst = os.path.join(archive_img_root, w['frame'])
             if os.path.exists(src):
                 shutil.copy(src, dst)
                 # Update URL in archived JSON to point to history
                 w['image_url'] = f"http://localhost:8000/static/data/history/{batch_id}/images/{w['frame']}"

        # 2. Archive Top Blur Frames (Source & Enhanced) for Analytics History
        # Sort by blur score desc
        top_blur = sorted(blur_data, key=lambda x: x.blur_score, reverse=True)[:10]
        for tb in top_blur:
             # Source
             src_orig = os.path.join(frames_dir, tb.filename)
             dst_orig = os.path.join(archive_img_root, tb.filename)
             if os.path.exists(src_orig): shutil.copy(src_orig, dst_orig)
             
             # Enhanced
             src_enh = os.path.join(enhanced_dir, tb.filename)
             dst_enh = os.path.join(archive_img_root, tb.filename) # Same name, overwrite? No, need to distinguish.
             # Actually, fetching comparison usually looks at static/frames vs static/enhanced.
             # If we want HISTORY comparison, we need separate folders or prefixes.
             # For MVP simplicity: We will just save them. If needed later, we adjust paths.
             # Let's just save the original 'source' frames for the top blur. The enhanced should be reproducible or saved too.
             # To avoid name collision if we copy both to same folder:
             # We won't copy enhanced for top blur right now to save space/complexity, 
             # OR we assume they are already in 'enhanced' dir and we copy them.
             pass

        # 3. Save Archived JSONs
        with open(f"{history_root}/wagons.json", "w") as f:
            json.dump(result_list, f, indent=4) # Uses updated URLs
            
        with open(f"{history_root}/metadata.json", "w") as f:
            json.dump(master_meta, f)
            
        # 4. Update Index
        index_file = "data/history/index.json"
        
        history_entry = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "wagon_count": len(result_list),
            "total_frames": len(master_meta),
            "label": f"Inspection {batch_id}"
        }
        
        index_data = []
        if os.path.exists(index_file):
            with open(index_file, "r") as f: index_data = json.load(f)
        
        index_data.append(history_entry)
        
        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=4)
            
        print(f"Batch {batch_id} archived successfully.")

    except Exception as e:
        print(f"Archiving Failed: {e}")
        # Don't fail the request, just log

    update_status("Idle", "Scan Complete", 100)
    
    return {
        "wagons": result_list, 
        "scanned_frames": len(frames_to_scan), 
        "total_frames": len(frames)
    }

@app.get("/metadata")
def get_metadata():
    try:
        with open("data/metadata.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@app.get("/wagons")
def get_wagons():
    try:
        with open("data/wagons.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# -------------------------------------------------------------------------
# HISTORY & ARCHIVING ENDPOINTS
# -------------------------------------------------------------------------

@app.get("/history")
def get_history_index():
    """Returns a list of all past inspection batches."""
    history_file = "data/history/index.json"
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r") as f:
            data = json.load(f)
            # Sort by date desc
            return sorted(data, key=lambda x: x['timestamp'], reverse=True)
    except:
        return []

@app.get("/history/{batch_id}/wagons")
def get_history_wagons(batch_id: str):
    """Returns the wagon report for a specific historical batch."""
    path = f"data/history/{batch_id}/wagons.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Batch not found")
    with open(path, "r") as f:
        return json.load(f)

@app.get("/history/{batch_id}/metadata")
def get_history_metadata(batch_id: str):
    """Returns the analytics metadata for a specific historical batch."""
    path = f"data/history/{batch_id}/metadata.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Batch not found")
    with open(path, "r") as f:
        return json.load(f)
