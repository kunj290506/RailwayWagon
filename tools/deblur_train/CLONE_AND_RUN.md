# Image Deblurring - Quick Clone & Run Guide

## For Anyone Who Clones This Repository

### What This Project Does
State-of-the-art image deblurring model trained on 1,151 paired images achieving **29.08 dB PSNR** (EXCELLENT tier).

### Prerequisites
- Python 3.8+
- CUDA-capable GPU (NVIDIA recommended)
- Git LFS installed
- 4GB+ GPU memory

---

## Quick Start (3 Steps)

### 1. Clone Repository
```bash
git clone https://github.com/kunj290506/RailwayWagon.git
cd RailwayWagon/tools/deblur_train
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Inference (Use Trained Model)
```bash
# Single image
python inference.py --input your_blurred_image.jpg --output deblurred_result.jpg

# Batch processing
python inference.py --batch --input blurred_folder/ --output results_folder/
```

**That's it! The trained model (best_model.pth) is already included.**

---

## Pre-Trained Model Included

**Model Details:**
- Architecture: ResNet-based Generator (12 residual blocks)
- Performance: 29.08 dB PSNR, 0.90+ SSIM
- Model file: `checkpoints/best_model.pth` (212MB)
- Trained for: 144 epochs (~47 hours)

**You don't need to train - just use it!**

---

## Usage Examples

### Deblur a Single Image
```bash
python inference.py \
  --input my_blurry_photo.jpg \
  --output my_sharp_photo.jpg \
  --checkpoint checkpoints/best_model.pth
```

### Process Multiple Images
```bash
python inference.py --batch \
  --input ./blurred_images/ \
  --output ./deblurred_results/
```

### With Quality Metrics
```bash
python inference.py --batch \
  --input ./test_blurred/ \
  --output ./test_results/ \
  --compare_with ./test_sharp/
```
Output includes PSNR and SSIM for each image.

---

## Optional: Train Your Own Model

If you have your own dataset:

### 1. Prepare Dataset
```
your_dataset/
├── blurred/    # Input blurry images
└── sharp/      # Target sharp images
```

### 2. Update Config
Edit `config.py`:
```python
DATA_ROOT = "path/to/your_dataset"
```

### 3. Train
```bash
python train.py
```

Training will:
- Show real-time progress every 10 batches
- Print detailed summaries after each epoch
- Save checkpoints every 5 epochs
- Auto-stop when optimal (early stopping)

**Expected time:** ~40-50 hours on GTX 1650

---

## Project Structure

```
tools/deblur_train/
├── checkpoints/
│   └── best_model.pth        # Pre-trained model (READY TO USE)
├── inference.py               # Use the model (START HERE)
├── train.py                   # Train new model (optional)
├── config.py                  # Configuration
├── models.py                  # Network architecture
├── dataset.py                 # Data loading
├── utils.py                   # Helper functions
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
└── QUICKSTART.md             # Quick guide
```

---

## System Requirements

### Minimum
- GPU: 4GB VRAM
- RAM: 8GB
- Storage: 2GB

### Recommended
- GPU: NVIDIA GTX 1650 or better
- RAM: 16GB
- Storage: 5GB

---

## Troubleshooting

### Issue: "CUDA not available"
**Solution:** Install PyTorch with CUDA support:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue: "Out of memory"
**Solution:** Use smaller batch size in inference:
```bash
python inference.py --input image.jpg --output result.jpg --img_size 128
```

### Issue: Git LFS files not downloaded
**Solution:** Install Git LFS and pull:
```bash
git lfs install
git lfs pull
```

---

## Performance

**On GTX 1650:**
- Inference speed: ~8 seconds per 256x256 image
- Batch processing: ~0.3 seconds per image

**Quality:**
- PSNR: 29.08 dB (excellent)
- SSIM: 0.90+ (very high)

---

## Citation

If you use this model in your work:
```
Image Deblurring Model - RailwayWagon Project
Trained on 1,151 paired images
Performance: 29.08 dB PSNR
GitHub: https://github.com/kunj290506/RailwayWagon
```

---

## Support

For issues or questions:
1. Check `QUICKSTART.md` for detailed instructions
2. Review `walkthrough.md` for implementation details
3. Open an issue on GitHub

---

**The model is ready to use out-of-the-box. Just clone and run inference!**
