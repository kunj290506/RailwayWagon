import os
from torch.utils.data import Dataset, random_split
from PIL import Image
import torchvision.transforms as transforms
import random

class DeblurDataset(Dataset):
    def __init__(self, root_dir, image_names=None, transform=None, mode='train', augment=False):
        """
        Args:
            root_dir (str): Path to the dataset root, e.g., 'C:/.../blurred_sharp/blurred_sharp'
                            Expects subdirectories 'blurred' and 'sharp'.
            image_names (list): List of image filenames to use. If None, uses all images.
            transform (callable, optional): Optional transform to be applied on a sample.
            mode (str): 'train' or 'val'.
            augment (bool): Whether to apply data augmentation (for training).
        """
        self.root_dir = root_dir
        self.transform = transform
        self.mode = mode
        self.augment = augment
        
        self.blur_dir = os.path.join(root_dir, 'blurred')
        self.sharp_dir = os.path.join(root_dir, 'sharp')
        
        if image_names is None:
            self.image_names = sorted([f for f in os.listdir(self.blur_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            # Simple verification
            sharp_files = set(os.listdir(self.sharp_dir))
            self.image_names = [f for f in self.image_names if f in sharp_files]
        else:
            self.image_names = image_names
        
        print(f"[{mode.upper()}] Loaded {len(self.image_names)} paired images")

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx]
        
        blur_path = os.path.join(self.blur_dir, img_name)
        sharp_path = os.path.join(self.sharp_dir, img_name)
        
        blur_img = Image.open(blur_path).convert('RGB')
        sharp_img = Image.open(sharp_path).convert('RGB')
        
        # Apply augmentation if enabled (for training)
        if self.augment:
            # Random horizontal flip
            if random.random() > 0.5:
                blur_img = transforms.functional.hflip(blur_img)
                sharp_img = transforms.functional.hflip(sharp_img)
            
            # Random rotation (small angles)
            if random.random() > 0.5:
                angle = random.uniform(-10, 10)
                blur_img = transforms.functional.rotate(blur_img, angle)
                sharp_img = transforms.functional.rotate(sharp_img, angle)
            
            # Random crop and resize (for better generalization)
            if random.random() > 0.3:
                i, j, h, w = transforms.RandomResizedCrop.get_params(
                    blur_img, scale=(0.8, 1.0), ratio=(0.95, 1.05)
                )
                blur_img = transforms.functional.resized_crop(blur_img, i, j, h, w, blur_img.size)
                sharp_img = transforms.functional.resized_crop(sharp_img, i, j, h, w, sharp_img.size)
        
        if self.transform:
            blur_img = self.transform(blur_img)
            sharp_img = self.transform(sharp_img)
        
        return blur_img, sharp_img

def create_train_val_datasets(root_dir, train_split=0.9, img_size=256, augment_train=True):
    """
    Create training and validation datasets with proper split
    Args:
        root_dir: Root directory containing 'blurred' and 'sharp' subdirectories
        train_split: Fraction of data to use for training (default: 0.9)
        img_size: Image size for resizing (default: 256)
        augment_train: Whether to augment training data (default: True)
    Returns:
        train_dataset, val_dataset
    """
    # Get all image names
    blur_dir = os.path.join(root_dir, 'blurred')
    all_images = sorted([f for f in os.listdir(blur_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    # Split into train and validation
    n_total = len(all_images)
    n_train = int(n_total * train_split)
    
    # Shuffle for random split
    random.seed(42)  # For reproducibility
    random.shuffle(all_images)
    
    train_images = all_images[:n_train]
    val_images = all_images[n_train:]
    
    # Create transform
    transform = get_transforms(img_size)
    
    # Create datasets
    train_dataset = DeblurDataset(
        root_dir=root_dir,
        image_names=train_images,
        transform=transform,
        mode='train',
        augment=augment_train
    )
    
    val_dataset = DeblurDataset(
        root_dir=root_dir,
        image_names=val_images,
        transform=transform,
        mode='val',
        augment=False
    )
    
    return train_dataset, val_dataset

def get_transforms(size=256):
    transform_list = [
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ]
    return transforms.Compose(transform_list)

class PairedTransform:
    def __init__(self, size=256):
        self.size = size
        self.transform = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        
    def __call__(self, blur, sharp):
        # Deterministic resize
        blur = self.transform(blur)
        sharp = self.transform(sharp)
        return blur, sharp
