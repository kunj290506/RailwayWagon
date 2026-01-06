"""
Enhanced Training Configuration for Superior Deblurring
Target: 32+ dB PSNR with Real-World Generalization
"""
import torch

class Config:
    # Dataset paths
    DATASET_ROOT = r"C:\Users\kunjc\Downloads\blurred_sharp\blurred_sharp"
    BLUR_DIR = "blurred"
    SHARP_DIR = "sharp"
    
    # Training parameters - OPTIMIZED FOR 32+ dB PSNR
    BATCH_SIZE = 6  # Slightly smaller for deeper model
    NUM_EPOCHS = 200  # More epochs for convergence 
    LEARNING_RATE_G = 5e-5  # Even lower for fine details
    LEARNING_RATE_D = 5e-5
    BETA1 = 0.9  # Higher for stable updates
    BETA2 = 0.999
    
    # Model parameters - DEEPER FOR BETTER QUALITY
    IMG_SIZE = 256
    IN_CHANNELS = 3
    OUT_CHANNELS = 3
    N_RESIDUAL_BLOCKS = 16  # Increased from 12 for deeper feature extraction
    
    # Loss weights - BALANCED FOR HIGH PSNR + PERCEPTUAL QUALITY
    LAMBDA_PIXEL = 200.0  # Higher for better PSNR
    LAMBDA_PERCEPTUAL = 3.0  # Stronger for realistic textures
    LAMBDA_ADV = 2.0  # Stronger for sharp edges
    
    # Learning rate scheduler - COSINE ANNEALING
    USE_SCHEDULER = True
    SCHEDULER_TYPE = "cosine"  # cosine annealing for smooth convergence
    MIN_LR = 1e-6
    
    # Training split
    TRAIN_SPLIT = 0.9
    
    # Checkpointing
    CHECKPOINT_DIR = "checkpoints"
    SAVE_FREQ = 10  # Save less frequently (only best)
    SAMPLE_FREQ = 5
    SAMPLE_DIR = "samples"
    
    # Logging
    LOG_DIR = "runs"
    PRINT_FREQ = 10
    
    # Device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    NUM_WORKERS = 4
    
    # Resume training
    RESUME = True  # Resume from best model to fine-tune
    RESUME_PATH = "checkpoints/best_model.pth"
    
    # Mixed precision training
    USE_AMP = True if torch.cuda.is_available() else False
    
    # Gradient clipping
    GRADIENT_CLIP = 1.0  # Stricter clipping
    
    # Early stopping
    EARLY_STOPPING_PATIENCE = 40  # More patience for deeper model
    MIN_DELTA = 0.001  # Very small delta for fine improvements
    
    # Advanced augmentation for better generalization
    USE_ADVANCED_AUG = True
    AUG_PROBABILITY = 0.5  # Apply augmentation to 50% of images
    
    # Data augmentation settings
    RANDOM_CROP = True
    RANDOM_FLIP = True
    RANDOM_ROTATION = True  # Up to 15 degrees
    COLOR_JITTER = True  # Slight brightness/contrast variation
    
    # Random seed
    SEED = 42
    
    # Test-time augmentation (TTA) for inference
    USE_TTA = True  # Average predictions from augmented versions
