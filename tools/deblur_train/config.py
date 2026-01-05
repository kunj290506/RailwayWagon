"""
Training Configuration for Image Deblurring
"""
import torch

class Config:
    # Dataset paths
    DATASET_ROOT = r"C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp"
    BLUR_DIR = "blurred"
    SHARP_DIR = "sharp"
    
    # Training parameters - OPTIMIZED FOR MAXIMUM ACCURACY
    BATCH_SIZE = 8  # Increased for better gradient estimates
    NUM_EPOCHS = 150  # More epochs for better convergence
    LEARNING_RATE_G = 1e-4  # Lower for more stable training
    LEARNING_RATE_D = 1e-4  # Lower for more stable training
    BETA1 = 0.5
    BETA2 = 0.999
    
    # Model parameters - ENHANCED FOR BETTER QUALITY
    IMG_SIZE = 256
    IN_CHANNELS = 3
    OUT_CHANNELS = 3
    N_RESIDUAL_BLOCKS = 12  # Increased from 9 for deeper model
    
    # Loss weights - OPTIMIZED FOR HIGHER PSNR & VISUAL QUALITY
    LAMBDA_PIXEL = 150.0  # Increased for better pixel accuracy
    LAMBDA_PERCEPTUAL = 2.0  # Increased for better textures
    LAMBDA_ADV = 1.5  # Increased for sharper images
    
    # Training split
    TRAIN_SPLIT = 0.9  # 90% training, 10% validation
    
    # Checkpointing
    CHECKPOINT_DIR = "checkpoints"
    SAVE_FREQ = 5  # Save checkpoint every N epochs
    SAMPLE_FREQ = 10  # Generate samples every N epochs
    SAMPLE_DIR = "samples"
    
    # Logging
    LOG_DIR = "runs"
    PRINT_FREQ = 10  # Print stats every N batches
    
    # Device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    NUM_WORKERS = 4
    
    # Resume training
    RESUME = False  # Set to True to resume from checkpoint
    RESUME_PATH = ""  # Path to checkpoint to resume from
    
    # Mixed precision training (for faster training on modern GPUs)
    USE_AMP = True if torch.cuda.is_available() else False
    
    # Gradient clipping
    GRADIENT_CLIP = 5.0  # Max gradient norm
    
    # Early stopping - ADJUSTED FOR LONGER TRAINING
    EARLY_STOPPING_PATIENCE = 30  # Increased patience for deeper model
    MIN_DELTA = 0.005  # Smaller delta for finer improvements
    
    # Advanced augmentation
    USE_ADVANCED_AUG = True  # Random crop, rotation, etc.
    
    # Random seed for reproducibility
    SEED = 42
