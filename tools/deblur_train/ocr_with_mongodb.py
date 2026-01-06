"""
Complete OCR Pipeline with MongoDB Integration
Usage: Process images and automatically save to MongoDB
"""
from wagon_ocr_pipeline import WagonNumberOCR
from wagon_ocr_mongodb import WagonOCRDatabase, process_and_save_to_db
import os
from tqdm import tqdm


def process_with_mongodb(image_path: str = None, folder_path: str = None, 
                         db_uri: str = None):
    """
    Process images with OCR and save to MongoDB
    
    Args:
        image_path: Single image path
        folder_path: Folder with images
        db_uri: MongoDB connection string
    """
    # Initialize OCR pipeline
    print("🚀 Initializing OCR Pipeline with MongoDB...")
    ocr = WagonNumberOCR(use_gpu=True)
    db = WagonOCRDatabase(connection_string=db_uri)
    
    if image_path:
        # Single image
        print(f"\n📸 Processing: {image_path}")
        doc_id = process_and_save_to_db(image_path, db, ocr)
        
        # Show result
        result = db.search_by_filename(os.path.basename(image_path))
        print(f"\n✅ Saved to MongoDB!")
        print(f"   Wagon Numbers: {result['wagon_numbers']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Document ID: {doc_id}")
        
    elif folder_path:
        # Batch processing
        image_files = [f for f in os.listdir(folder_path)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"\n📁 Processing {len(image_files)} images from {folder_path}")
        
        for image_file in tqdm(image_files, desc="Processing"):
            image_path = os.path.join(folder_path, image_file)
            
            try:
                process_and_save_to_db(image_path, db, ocr)
            except Exception as e:
                print(f"   ❌ Error processing {image_file}: {e}")
        
        # Show statistics
        print("\n" + "="*60)
        stats = db.get_statistics()
        print(f"✅ Batch Complete!")
        print(f"   Total processed: {stats['total_images']}")
        print(f"   Wagon numbers found: {stats['unique_wagon_numbers']}")
        print(f"   Average confidence: {stats['average_confidence']:.1%}")
        print("="*60 + "\n")
    
    else:
        print("❌ Specify --image or --folder")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR Pipeline with MongoDB')
    parser.add_argument('--image', type=str, help='Single image path')
    parser.add_argument('--folder', type=str, help='Folder with images')
    parser.add_argument('--db-uri', type=str, help='MongoDB URI')
    
    args = parser.parse_args()
    
    process_with_mongodb(
        image_path=args.image,
        folder_path=args.folder,
        db_uri=args.db_uri
    )
