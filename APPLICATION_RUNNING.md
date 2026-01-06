# Railway Wagon Detection System - Running

## 🚀 Application Started!

### Access URLs:
- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ✅ What's Running:

### 1. Backend Server (Port 8000)
- FastAPI application
- OCR endpoints
- Video processing
- MongoDB integration

### 2. Frontend Dashboard (Port 5173)
- React application
- Real-time detection results
- Batch processing interface

---

## 🔧 New OCR Features Available:

### Dual-Mode OCR:
1. **Wagon Mode** (11-digit rule) - Default
2. **Normal Mode** (all text detection)

### Test OCR from Command Line:
```bash
cd d:\adani\tools\deblur_train

# Test wagon mode
python test_dual_mode.py path/to/image.jpg --mode wagon

# Test normal mode
python test_dual_mode.py path/to/image.jpg --mode normal

# Compare both
python test_dual_mode.py path/to/image.jpg --mode compare
```

---

## 📊 MongoDB Database:
Make sure MongoDB is running for OCR result storage:
```bash
# If using Docker:
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or start MongoDB service on Windows
net start MongoDB
```

---

## 🎯 Quick Test:

### 1. Open Browser
- Navigate to: http://localhost:5173
- You should see the Railway Wagon Detection Dashboard

### 2. Upload Image/Video
- Use the upload interface
- Select wagon mode or normal mode
- View OCR results in real-time

### 3. Check API
- Open: http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly

---

## 🛠 Troubleshooting:

### Port Already in Use?
```bash
# Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Kill process if needed
taskkill /PID [PID_NUMBER] /F
```

### Frontend Not Loading?
```bash
cd d:\adani\frontend
npm install
npm run dev
```

### Backend Error?
```bash
cd d:\adani
python -m uvicorn backend.app:app --reload --port 8000
```

---

## 📝 Summary:

✅ Backend: Running on port 8000  
✅ Frontend: Running on port 5173  
✅ OCR Pipeline: Deblur + PaddleOCR ready  
✅ MongoDB: Optional (for storing results)  
✅ Dual-Mode: Wagon (11-digit) + Normal (all text)  

**Ready to detect wagon numbers!** 🚂
