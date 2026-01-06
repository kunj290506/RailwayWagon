"""
High Quality Training Configuration
Target: 32+ dB PSNR, 0.92+ SSIM
"""
import torch

class Config:
    # Dataset paths
    DATASET_ROOT = r"C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp"
    BLUR_DIR = "blurred"
    SHARP_DIR = "sharp"
    
    # Training parameters - Quality over speed
    BATCH_SIZE = 8
    NUM_EPOCHS = 250  # Extended for better convergence
    LEARNING_RATE_G = 5e-5  # Low for fine details
    LEARNING_RATE_D = 5e-5
    BETA1 = 0.9
    BETA2 = 0.999
    
    # Model parameters - Deep for quality
    IMG_SIZE = 256
    IN_CHANNELS = 3
    OUT_CHANNELS = 3
    N_RESIDUAL_BLOCKS = 16  # Deep model
    
    # Loss weights - Optimized for PSNR + SSIM
    LAMBDA_PIXEL = 250.0  # Higher for better PSNR
    LAMBDA_PERCEPTUAL = 4.0  # Higher for better SSIM
    LAMBDA_ADV = 2.5  # Sharper edges
    
    # Training split
    TRAIN_SPLIT = 0.9
    
    # Checkpointing
    CHECKPOINT_DIR = "checkpoints"
    SAVE_FREQ = 5
    SAMPLE_FREQ = 5
    SAMPLE_DIR = "samples"
    
    # Logging
    LOG_DIR = "runs"
    PRINT_FREQ = 10
    
    # Device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    NUM_WORKERS = 4
    
    # Resume from previous best
    RESUME = True
    RESUME_PATH = "checkpoints/best_model1.pth"
    
    # Mixed precision
    USE_AMP = True
    
    # Gradient clipping
    GRADIENT_CLIP = 1.0
    
    # Early stopping - Stop only at target
    EARLY_STOPPING_PATIENCE = 50
    MIN_DELTA = 0.001
    
    # Augmentation
    USE_ADVANCED_AUG = True
    
    # Random seed
    SEED = 42
