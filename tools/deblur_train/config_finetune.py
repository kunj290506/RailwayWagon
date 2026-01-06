"""
Optimized Fine-Tuning Configuration
Target: >32 dB PSNR, >0.95 SSIM
Supports: NVIDIA Jetson deployment
"""
import torch

class Config:
    # Dataset paths
    DATASET_ROOT = r"C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp"
    BLUR_DIR = "blurred"
    SHARP_DIR = "sharp"
    
    # Fine-tuning parameters - ULTRA-PRECISE
    BATCH_SIZE = 4  # Smaller for more stable gradients
    NUM_EPOCHS = 200  # Full training with optimized config
    LEARNING_RATE_G = 2e-4  # Standard initial LR, will decay with cosine
    LEARNING_RATE_D = 2e-4
    BETA1 = 0.9
    BETA2 = 0.999
    
    # Model parameters
    IMG_SIZE = 256
    IN_CHANNELS = 3
    OUT_CHANNELS = 3
    N_RESIDUAL_BLOCKS = 9  # Match checkpoint architecture (was trained with 9)
    
    # Loss weights - OPTIMIZED FOR HIGH PSNR + SSIM
    LAMBDA_PIXEL = 300.0  # Increased from 200 - stronger PSNR focus
    LAMBDA_PERCEPTUAL = 5.0  # Increased from 3 - better SSIM
    LAMBDA_ADV = 1.5  # Decreased from 2 - less aggressive for stability
    LAMBDA_SSIM = 2.0  # NEW: Direct SSIM optimization
    
    # Training split
    TRAIN_SPLIT = 0.9
    
    # Checkpointing
    CHECKPOINT_DIR = "checkpoints"
    SAVE_FREQ = 5  # Save every 5 epochs for fine-tuning
    SAMPLE_FREQ = 5
    SAMPLE_DIR = "samples"
    
    # Logging
    LOG_DIR = "runs_finetune"
    PRINT_FREQ = 10
    
    # Device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    NUM_WORKERS = 4
    
    # Training from scratch with optimized parameters
    # This configuration is better than the checkpoint anyway
    RESUME = False
    RESUME_PATH = ""  # Train from scratch
    
    # Mixed precision - Essential for Jetson compatibility
    USE_AMP = True if torch.cuda.is_available() else False
    
    # Gradient clipping - Tighter for fine-tuning
    GRADIENT_CLIP = 0.5  # More conservative than 1.0
    
    # Early stopping - Only stop if training plateaus
    EARLY_STOPPING_PATIENCE = 50  # Increased for maximum quality
    MIN_DELTA = 0.0001  # Very small delta for fine-tuning
    TARGET_PSNR = 32.0  # Reference target
    TARGET_SSIM = 0.95  # Reference target (won't stop training when achieved)
    
    # Learning rate scheduler - Cosine annealing with warm restarts
    USE_SCHEDULER = True
    SCHEDULER_TYPE = "cosine_warmrestart"
    COSINE_T0 = 20  # Initial restart period
    COSINE_TMULT = 2  # Period multiplier
    MIN_LR = 1e-7  # Minimum learning rate
    
    # Augmentation - Enhanced for generalization
    USE_ADVANCED_AUG = True
    AUG_PROBABILITY = 0.5
    RANDOM_CROP = True
    RANDOM_FLIP = True
    RANDOM_ROTATION = True
    COLOR_JITTER = True
    
    # Discriminator freezing strategy
    FREEZE_DISCRIMINATOR_EPOCHS = 20  # Freeze D for first 20 epochs
    
    # SSIM Loss integration
    USE_SSIM_LOSS = True  # Enable MS-SSIM loss component
    
    # Jetson deployment flags
    JETSON_COMPATIBLE = True  # Enable Jetson-compatible export
    EXPORT_TORCHSCRIPT = True  # Export to TorchScript
    ENABLE_FP16_EXPORT = True  # Enable FP16 for Jetson
    
    # Random seed
    SEED = 42
    
    # Progress tracking
    MONITOR_HISTORY = "checkpoints/training_history_finetune.json"
