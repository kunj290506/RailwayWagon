# Training Quick Start Guide

## Current Training Status

**Training Mode**: From scratch with optimized configuration  
**Started**: Just now  
**Configuration File**: `config_finetune.py`  
**Training Script**: `train_finetune.py`

## Optimizations Applied

### 1. Enhanced Loss Functions
- **Pixel Loss Weight**: 300.0 (vs 200.0 before) - stronger PSNR emphasis
- **Perceptual Loss Weight**: 5.0 (vs 3.0 before) - better SSIM/quality
- **SSIM Loss Weight**: 2.0 (NEW) - direct structural similarity optimization
- **Adversarial Loss Weight**: 1.5 (vs 2.0 before) - reduced for stability

### 2. Training Strategy
- **Discriminator Freezing**: First 20 epochs focus purely on generator quality
- **Cosine Annealing**: Learning rate scheduler with warm restarts (T0=20, Tmult=2)
- **Gradient Clipping**: 0.5 (tighter than before for stability)
- **Batch Size**: 4 (smaller for more stable updates)

### 3. Targets
- **PSNR**: >32 dB (currently at 29.08 dB, need +2.92 dB)
- **SSIM**: >0.95 (currently at 0.865, need +0.085)

## Monitoring Training

### Real-time Monitor
Open a new terminal and run:
```bash
cd d:\adani\tools\deblur_train
python monitor_cli.py --history checkpoints/training_history_finetune.json --refresh 5
```

This will show:
- Current epoch and progress
- Latest PSNR and SSIM scores
- Best results so far
- Progress towards 32 dB target

### TensorBoard (Optional)
```bash
cd d:\adani\tools\deblur_train
tensorboard --logdir=runs_finetune
```
Then open http://localhost:6006

## Training Timeline

- **Epoch Duration**: ~2-3 minutes per epoch
- **Total Training Time**: Estimated 6-10 hours for 200 epochs
- **Early Stopping**: Will stop automatically if targets (32 dB, 0.95 SSIM) are achieved
- **Patience**: 30 epochs without improvement before early stopping

## Checkpoints

Checkpoints are saved in `d:\adani\tools\deblur_train\checkpoints\`:
- `finetune_epoch_XXX.pth` - Regular checkpoints every 5 epochs
- `best_model_finetune.pth` - Best model so far (use this for inference)

## Sample Images

Sample deblurred images are generated every 5 epochs in:
`d:\adani\tools\deblur_train\samples\`

## After Training Completes

### 1. Evaluate Final Model
```bash
python check_model.py --checkpoint checkpoints/best_model_finetune.pth
```

### 2. Export for Jetson Deployment
```bash
python export_jetson.py --checkpoint checkpoints/best_model_finetune.pth --fp16 --benchmark
```

This creates optimized models in `jetson_export/`:
- `model_jetson.pt` - TorchScript version (FP32)
- `model_jetson_fp16.pth` - FP16 version for Jetson
- `README_JETSON.md` - Deployment guide

### 3. Test Inference
```bash
python inference.py --checkpoint checkpoints/best_model_finetune.pth --input path/to/blurred.jpg --output deblurred.jpg
```

## Notes

- Training is running in the background
- You can close this window - training will continue
- Check progress anytime with the monitor script
- Training will auto-save best model and stop when targets are met
