import requests
import time
import os
import json

API_URL = "http://localhost:8000"

VIDEO_PATHS = [
    r"C:\Users\kunjc\Videos\output_video3.mp4",
    r"C:\Users\kunjc\Videos\output_video.mp4",
    r"C:\Users\kunjc\Videos\output_video1.mp4",
    r"C:\Users\kunjc\Videos\output_video2.mp4"
]

def run_batch_via_api():
    print("=========================================================")
    print("   ADANI AI: BATCH VALIDATION (Via Localhost API)")
    print("=========================================================")
    
    overall_report = []

    for idx, vid_path in enumerate(VIDEO_PATHS):
        print(f"\n🎥 [VIDEO {idx+1}/{len(VIDEO_PATHS)}]: {vid_path}")
        
        if not os.path.exists(vid_path):
            print(f"   ❌ File not found locally.")
            continue
            
        try:
            # 1. Upload & Extract
            print("   -> Uploading & Extracting Frames...", end="", flush=True)
            with open(vid_path, 'rb') as f:
                t0 = time.time()
                resp = requests.post(f"{API_URL}/upload_video", files={'file': f})
                if resp.status_code != 200:
                    print(f" Failed! {resp.text}")
                    continue
                print(f" Done ({resp.json().get('frames_extracted')} frames in {time.time()-t0:.1f}s)")

            # 2. Analyze Blur
            print("   -> Analyzing Blur Quality...", end="", flush=True)
            resp = requests.post(f"{API_URL}/analyze_blur")
            if resp.status_code == 200:
                data = resp.json()
                print(f" Done (Avg Score: {data.get('avg_blur_score')})")
            else:
                print(" Failed!")

            # 3. Enhance (GPU)
            print("   -> Enhancing Frames (GPU)...", end="", flush=True)
            # This is synchronous/blocking on the server usually for this demo code
            t0 = time.time()
            resp = requests.post(f"{API_URL}/enhance_frames")
            if resp.status_code == 200:
                print(f" Done ({time.time()-t0:.1f}s)")
            else:
                print(f" Failed! {resp.text}")

            # 4. Scan Wagons (OCR)
            print("   -> Scanning for Wagons...", end="", flush=True)
            t0 = time.time()
            resp = requests.post(f"{API_URL}/scan_wagons")
            if resp.status_code == 200:
                data = resp.json()
                wagons = data.get("wagons", [])
                print(f" Done! Found {len(wagons)} Wagons.")
                
                # Print details
                for w in wagons:
                    print(f"      ✅ Wagon: {w.get('number')} | Conf: {int(w.get('confidence',0)*100)}% | Frame: {w.get('frame')}")
                
                overall_report.append({
                    "video": vid_path,
                    "wagons": wagons
                })
            else:
                print(f" Failed! {resp.text}")
                
        except Exception as e:
            print(f"\n   ❌ Critical execution error: {e}")

    # Save
    with open("batch_report_final.json", "w") as f:
        json.dump(overall_report, f, indent=4)
        
    print("\n=========================================================")
    print("   BATCH COMPLETE - See batch_report_final.json")
    print("=========================================================")

if __name__ == "__main__":
    run_batch_via_api()
