# TRAINING COMMAND - WITH DETAILED OUTPUT

## STOP ALL TASKS:
```powershell
taskkill /F /IM python.exe
```

## START FRESH TRAINING:
```powershell
cd d:\adani\tools\deblur_train
python train.py
```

## WHAT YOU'LL SEE:

### 1. During Epoch (every 10 batches):
```
Epoch 0 | Batch 0/130 | G_loss: 22.4521 | D_loss: 0.4123 | L1: 0.2145 | Perc: 0.8234 | Adv: 0.7123
Epoch 0 | Batch 10/130 | G_loss: 21.3412 | D_loss: 0.3921 | L1: 0.2034 | Perc: 0.7921 | Adv: 0.6834
Epoch 0 | Batch 20/130 | G_loss: 20.2341 | D_loss: 0.3712 | L1: 0.1923 | Perc: 0.7623 | Adv: 0.6523
```

### 2. After Epoch Completes:
```
================================================================================
EPOCH 0/149 COMPLETED
================================================================================

TIME INFORMATION:
  This epoch:        945.2 seconds (15.8 minutes)
  Total elapsed:     0.26 hours
  Average per epoch: 15.8 minutes
  Estimated remain:  39.3 hours
  Progress:          1/150 (0.7%)

TRAINING LOSSES:
  Generator Loss:    18.365454
  Discriminator Loss: 0.172065
  L1 Loss:           0.168688
  Perceptual Loss:   0.731654
  Adversarial Loss:  0.764952

VALIDATION METRICS:
  PSNR:  20.3917 dB
  SSIM:  0.677334

LEARNING RATES:
  Generator:     0.000100
  Discriminator: 0.000100
================================================================================
```

## TRAINING CONFIGURATION:
- 150 epochs
- 12 residual blocks (optimized for maximum accuracy)
- Batch size: 8
- Detailed output every 10 batches + full summary per epoch
- Time estimates included

## JUST RUN:
```powershell
cd d:\adani\tools\deblur_train
python train.py
```

That's it! All output will appear directly in your terminal.
