# Image Deblurring Model - Contest Ready 🏆

Professional training pipeline for transforming blurred images to sharp images using deep learning.

## ✨ Features

- **Multi-Loss Training**: L1 + Perceptual (VGG19) + Adversarial loss
- **Detailed Metrics**: PSNR, SSIM, and all loss components tracked per epoch
- **TensorBoard Integration**: Real-time training visualization
- **Automatic Checkpointing**: Save best models based on validation PSNR
- **Sample Generation**: Visual comparison of results during training
- **Resume Training**: Continue from checkpoints
- **Mixed Precision**: Faster training on modern GPUs

## 📁 Files

- **train.py** - Main training script with comprehensive logging
- **config.py** - Training configuration and hyperparameters
- **dataset.py** - Dataset loader with train/val split and augmentation
- **models.py** - Neural network architectures (Generator & Discriminator)
- **utils.py** - Metrics calculation and visualization utilities
- **evaluate.py** - Model evaluation with PSNR/SSIM
- **inference.py** - Deblur single images

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Training
```bash
# Full training (100 epochs)
python train.py

# Quick test (1 epoch)
python train.py --epochs 1 --batch_size 2

# Custom configuration
python train.py --epochs 50 --batch_size 8
```

### 3. Monitor Progress
```bash
# Launch TensorBoard
tensorboard --logdir=runs
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 🎯 Expected Results

- **Target PSNR**: ~28-32 dB
- **Target SSIM**: >0.85
- **Training Time**: ~2-4 hours on GPU

## 📊 Metrics Tracked Per Epoch

1. **Generator Loss** (total)
2. **Discriminator Loss**
3. **L1 Loss** (pixel-wise)
4. **Perceptual Loss** (VGG19 features)
5. **Adversarial Loss**
6. **PSNR** (Peak Signal-to-Noise Ratio)
7. **SSIM** (Structural Similarity Index)
8. **Learning Rates**

## 📁 Dataset

- Input (blurred): `C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp\blurred`
- Output (sharp): `C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp\sharp`
- Total pairs: 1,151 images
- Split: 90% training (1,035), 10% validation (116)

## 🏗️ Architecture

**Generator**: ResNet-based with 9 residual blocks
- Encoder-decoder structure
- Instance normalization
- Reflection padding

**Discriminator**: Conditional PatchGAN
- Distinguishes real vs generated sharp images

**Feature Extractor**: VGG19 (pretrained)
- For perceptual loss calculation

## 📦 Output Structure

```
checkpoints/
├── best_model.pth           # Best model (highest PSNR)
├── checkpoint_epoch_*.pth   # Regular checkpoints
├── training_history.json    # All metrics
└── training_history.png     # Metric plots

samples/
├── epoch_009.png            # Visual comparisons
└── ...

runs/
└── [TensorBoard logs]
```

## 🔧 Configuration

Edit `config.py` to customize:
- Batch size: 4 (adjust based on GPU memory)
- Learning rate: 2e-4
- Image size: 256x256
- Loss weights
- Number of epochs
- And more...

## 📈 Usage Examples

### Training
```bash
python train.py
```

### Evaluation
```bash
python evaluate.py
```

### Inference
```bash
python inference.py
```

## 🏆 Contest Tips

1. Train for **100 epochs** for best results
2. Monitor **PSNR** - key metric for deblurring
3. Use **best_model.pth** for final submission
4. Check **sample images** to verify visual quality
5. Save **training_history.json** for documentation

## 📊 TensorBoard Visualization

Real-time monitoring includes:
- Loss curves (all components)
- PSNR and SSIM trends
- Sample image comparisons
- Learning rate schedules

## 🛠️ Troubleshooting

**Out of Memory**: Reduce `BATCH_SIZE` in config.py
**Slow Training**: Ensure GPU is being used, check console output
**Poor Results**: Train longer, adjust loss weights

---

**Good luck with your contest!** 🎉
