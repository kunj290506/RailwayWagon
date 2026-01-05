# Image Deblurring Training - Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Dataset
Your dataset is already configured:
- **Blurred Images**: `C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp\blurred`
- **Sharp Images**: `C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp\sharp`
- **Total Pairs**: 1,151 images

### 3. Start Training

#### Full Training (100 epochs)
```bash
python train.py
```

#### Quick Test (1 epoch)
```bash
python train.py --epochs 1 --batch_size 2
```

#### Custom Configuration
```bash
python train.py --epochs 50 --batch_size 8
```

### 4. Monitor Training

#### TensorBoard (Real-time Monitoring)
```bash
tensorboard --logdir=runs
```
Then open http://localhost:6006 in your browser

#### Console Output
The script prints detailed metrics every epoch:
- Generator Loss
- Discriminator Loss
- L1 Loss (pixel-wise)
- Perceptual Loss
- Adversarial Loss
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index)
- Learning Rates

## 📊 What You'll Get

### During Training:
1. **Console logs** with epoch-by-epoch detailed metrics
2. **TensorBoard visualizations** of:
   - All loss curves
   - PSNR/SSIM metrics
   - Sample image comparisons
3. **Checkpoints** saved every 5 epochs in `checkpoints/`
4. **Sample images** every 10 epochs in `samples/`
5. **Best model** automatically saved as `checkpoints/best_model.pth`

### After Training:
1. **training_history.json** - All metrics in JSON format
2. **training_history.png** - Loss and metric plots
3. **Best model checkpoint** with highest PSNR

## 🎯 Expected Results

- **Baseline PSNR**: ~20-25 dB (simple models)
- **Target PSNR**: ~28-32 dB (with our multi-loss approach)
- **Target SSIM**: >0.85
- **Training Time**: ~2-4 hours on GPU

## 📁 Output Structure

```
deblur_train/
├── checkpoints/
│   ├── best_model.pth              # Best model
│   ├── checkpoint_epoch_004.pth    # Regular checkpoints
│   ├── checkpoint_epoch_009.pth
│   ├── training_history.json       # All metrics
│   └── training_history.png        # Metric plots
├── samples/
│   ├── epoch_009.png               # Visual comparisons
│   ├── epoch_019.png
│   └── ...
└── runs/
    └── [tensorboard logs]
```

## 🔧 Advanced Options

### Resume Training
```bash
python train.py --resume checkpoints/checkpoint_epoch_049.pth
```

### Adjust Hyperparameters
Edit `config.py` to modify:
- Batch size
- Learning rates
- Loss weights
- Image size
- Number of residual blocks
- And more...

## 📈 Understanding the Metrics

### PSNR (Peak Signal-to-Noise Ratio)
- Higher is better
- Measured in dB
- >30 dB is excellent for deblurring

### SSIM (Structural Similarity Index)
- Range: 0 to 1
- Higher is better
- >0.85 indicates good structural similarity

### Losses:
- **Generator Loss**: Total loss for image generation
- **L1 Loss**: Pixel-wise difference
- **Perceptual Loss**: High-level feature similarity (VGG19)
- **Adversarial Loss**: Helps generate sharper, more realistic images
- **Discriminator Loss**: How well it distinguishes real vs fake

## 🏆 Contest Tips

1. **Train for 100 epochs** for best results
2. **Monitor PSNR** - this is often the key metric for deblurring contests
3. **Check sample images** to ensure visual quality
4. **Use best_model.pth** for final submissions
5. **Document your training** - save the training_history.json

## 🛠️ Troubleshooting

### Out of Memory Error
Reduce batch size in `config.py`:
```python
BATCH_SIZE = 2  # or even 1
```

### Slow Training
- Ensure you're using GPU (check console output)
- Reduce image size in `config.py` (e.g., 128 instead of 256)
- Disable mixed precision: `USE_AMP = False`

### Poor Results
- Train longer (more epochs)
- Adjust loss weights in `config.py`
- Check TensorBoard for loss convergence

## 📞 Files Overview

- **train.py** - Main training script
- **config.py** - All configuration parameters
- **models.py** - Generator and Discriminator architectures
- **dataset.py** - Dataset loading with train/val split
- **utils.py** - Helper functions for metrics and visualization
- **evaluate.py** - Standalone evaluation script
- **inference.py** - Run inference on new images

Good luck with your contest! 🎉
