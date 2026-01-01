# AI-Based Real-Time Railway Wagon Inspection System

An MVP solution for detecting motion blur, enhancing low-light frames, and improving OCR accuracy on fast-moving railway wagons.

## 📂 Project Structure

- `backend/`: FastAPI server with Computer Vision & AI logic.
- `frontend/`: React Dashboard for visualization and analytics.
- `data/`: Scripts to generate synthetic testing data.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+

### 1. Setup & Generate Data
First, generate the synthetic video sample if you don't have real footage.
```bash
# Install Python dependencies (from root)
pip install -r backend/requirements.txt

# Run Generator
python data/sample_generator.py
# This creates data/sample_video.mp4
```

### 2. Run Backend
Start the FastAPI server.
```bash
# From root directory
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```
*   API Docs: `http://localhost:8000/docs`
*   The backend will store processed images in `backend/static`.

### 3. Run Frontend
Start the React Dashboard.
```bash
cd frontend
npm install
npm run dev
```
*   Open `http://localhost:5173` in your browser.

## 🌟 Features & Usage

1.  **Upload Video**: Click the upload area and select `data/sample_video.mp4`.
2.  **Processing**: The backend analyzes blur, enhances frames, and runs OCR.
3.  **Dashboard**:
    *   **Frame Viewer**: Compare "Original" vs "Enhanced" side-by-side. Notice how the text becomes readable in the enhanced version.
    *   **Metrics**: View the blur score timeline.
4.  **Top 10 Corrected**: Click the "View Top 10 Corrected" button to see the frames where AI enhancement made the biggest difference.

## 🔧 AI Explanation
- **Blur Detection**: Uses Laplacian Variance. Scores < 50 are considered "High Blur".
- **Enhancement**: 
    - **CLAHE** (Contrast Limited Adaptive Histogram Equalization) for low-light details.
    - **Sharpening Kernel** to reduce motion blur.
- **AI Models**:
    - **PaddleOCR** for text reading.
    - **YOLOv8** for wagon detection.
    - *Note: If these libraries fail to load (e.g. missing drivers), the system gracefully falls back to a Mock mode for demo purposes.*

## 📸 Demo Tips
- Use the generated `sample_video.mp4` for the best "Before/After" demonstration as it is tuned to show the capabilities of the specific algorithms implemented.
