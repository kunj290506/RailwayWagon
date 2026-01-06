"""
MongoDB Integration for Wagon OCR Results
Store and query OCR results in MongoDB
"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os


class WagonOCRDatabase:
    """
    MongoDB database for storing wagon OCR results
    """
    
    def __init__(self, connection_string: str = None, db_name: str = "wagon_ocr"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB URI (default: localhost)
            db_name: Database name
        """
        if connection_string is None:
            connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        
        # Collections
        self.ocr_results = self.db['ocr_results']
        self.wagon_numbers = self.db['wagon_numbers']
        
        # Create indexes for faster queries
        self._create_indexes()
        
        print(f"✅ Connected to MongoDB: {db_name}")
    
    def _create_indexes(self):
        """Create database indexes"""
        # Index on wagon numbers for fast lookup
        self.ocr_results.create_index('wagon_numbers')
        self.ocr_results.create_index('timestamp')
        self.ocr_results.create_index('filename')
        
        # Unique index on wagon number + last_seen for wagon_numbers collection
        self.wagon_numbers.create_index('number', unique=True)
    
    def save_ocr_result(self, result: Dict) -> str:
        """
        Save OCR result to database
        
        Args:
            result: OCR result dictionary from pipeline
        
        Returns:
            Inserted document ID
        """
        doc = {
            'filename': result.get('filename', 'unknown'),
            'wagon_numbers': result.get('wagon_numbers', []),
            'all_text': result.get('all_text', ''),
            'confidence': result.get('confidence', 0.0),
            'num_detected': len(result.get('wagon_numbers', [])),
            'timestamp': datetime.utcnow(),
            'status': result.get('status', 'success'),
            'metadata': {
                'image_path': result.get('image_path', ''),
                'processing_time': result.get('processing_time', 0.0),
                'ocr_engine': result.get('ocr_engine', 'unknown')
            }
        }
        
        # Insert result
        insert_result = self.ocr_results.insert_one(doc)
        
        # Update wagon numbers collection
        for wagon_num in result.get('wagon_numbers', []):
            self._update_wagon_number(wagon_num, result.get('filename', ''))
        
        return str(insert_result.inserted_id)
    
    def _update_wagon_number(self, wagon_number: str, filename: str):
        """Update or create wagon number entry"""
        self.wagon_numbers.update_one(
            {'number': wagon_number},
            {
                '$set': {
                    'last_seen': datetime.utcnow(),
                    'last_filename': filename
                },
                '$inc': {'count': 1},
                '$setOnInsert': {'first_seen': datetime.utcnow()}
            },
            upsert=True
        )
    
    def search_by_wagon_number(self, wagon_number: str) -> List[Dict]:
        """
        Search for all images containing a wagon number
        
        Args:
            wagon_number: Wagon number to search for
        
        Returns:
            List of matching OCR results
        """
        results = self.ocr_results.find(
            {'wagon_numbers': wagon_number}
        ).sort('timestamp', -1)
        
        return list(results)
    
    def search_by_filename(self, filename: str) -> Optional[Dict]:
        """
        Get OCR result for a specific filename
        
        Args:
            filename: Image filename
        
        Returns:
            OCR result or None
        """
        return self.ocr_results.find_one({'filename': filename})
    
    def get_recent_results(self, limit: int = 50) -> List[Dict]:
        """
        Get most recent OCR results
        
        Args:
            limit: Number of results to return
        
        Returns:
            List of recent OCR results
        """
        results = self.ocr_results.find().sort('timestamp', -1).limit(limit)
        return list(results)
    
    def get_all_wagon_numbers(self) -> List[Dict]:
        """
        Get all unique wagon numbers with statistics
        
        Returns:
            List of wagon numbers with count and last seen
        """
        wagon_nums = self.wagon_numbers.find().sort('last_seen', -1)
        return list(wagon_nums)
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Statistics dictionary
        """
        total_images = self.ocr_results.count_documents({})
        successful = self.ocr_results.count_documents({'status': 'success'})
        total_wagon_numbers = self.wagon_numbers.count_documents({})
        
        # Average confidence
        pipeline = [
            {'$match': {'status': 'success'}},
            {'$group': {
                '_id': None,
                'avg_confidence': {'$avg': '$confidence'}
            }}
        ]
        avg_result = list(self.ocr_results.aggregate(pipeline))
        avg_confidence = avg_result[0]['avg_confidence'] if avg_result else 0.0
        
        return {
            'total_images': total_images,
            'successful_detections': successful,
            'failed_detections': total_images - successful,
            'unique_wagon_numbers': total_wagon_numbers,
            'average_confidence': avg_confidence
        }
    
    def batch_import_csv(self, csv_path: str):
        """
        Import existing CSV results into MongoDB
        
        Args:
            csv_path: Path to CSV file
        """
        import pandas as pd
        
        df = pd.read_csv(csv_path)
        
        imported = 0
        for _, row in df.iterrows():
            wagon_nums = str(row.get('wagon_numbers', '')).split(', ') if row.get('wagon_numbers') else []
            wagon_nums = [w.strip() for w in wagon_nums if w.strip()]
            
            result = {
                'filename': row.get('filename', ''),
                'wagon_numbers': wagon_nums,
                'all_text': row.get('all_text', ''),
                'confidence': float(row.get('confidence', 0.0)),
                'status': row.get('status', 'success')
            }
            
            self.save_ocr_result(result)
            imported += 1
        
        print(f"✅ Imported {imported} results from CSV")
    
    def export_to_csv(self, output_path: str):
        """
        Export database to CSV
        
        Args:
            output_path: Output CSV path
        """
        import pandas as pd
        
        results = self.get_recent_results(limit=10000)
        
        data = []
        for r in results:
            data.append({
                'filename': r['filename'],
                'wagon_numbers': ', '.join(r['wagon_numbers']),
                'num_detected': r['num_detected'],
                'confidence': r['confidence'],
                'timestamp': r['timestamp'],
                'status': r['status']
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        print(f"✅ Exported {len(data)} results to {output_path}")


# =============================================================================
# INTEGRATION WITH OCR PIPELINE
# =============================================================================

def process_and_save_to_db(image_path: str, db: WagonOCRDatabase, ocr_pipeline):
    """
    Process image and save result to MongoDB
    
    Args:
        image_path: Path to image
        db: WagonOCRDatabase instance
        ocr_pipeline: WagonNumberOCR instance
    
    Returns:
        Document ID
    """
    import time
    
    start_time = time.time()
    
    # Process image with OCR pipeline
    result = ocr_pipeline.process_image(image_path)
    
    processing_time = time.time() - start_time
    
    # Add metadata
    result['filename'] = os.path.basename(image_path)
    result['image_path'] = image_path
    result['processing_time'] = processing_time
    result['ocr_engine'] = ocr_pipeline.ocr_type
    result['status'] = 'success'
    
    # Save to database
    doc_id = db.save_ocr_result(result)
    
    print(f"✅ Saved to MongoDB: {result['filename']} → {result['wagon_numbers']}")
    
    return doc_id


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MongoDB Integration for Wagon OCR')
    parser.add_argument('--setup', action='store_true', help='Setup database')
    parser.add_argument('--import-csv', type=str, help='Import CSV file')
    parser.add_argument('--export-csv', type=str, help='Export to CSV file')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--search', type=str, help='Search for wagon number')
    parser.add_argument('--recent', type=int, default=10, help='Show recent results')
    parser.add_argument('--db-uri', type=str, help='MongoDB connection string')
    
    args = parser.parse_args()
    
    # Connect to MongoDB
    db = WagonOCRDatabase(connection_string=args.db_uri)
    
    if args.setup:
        print("\n✅ Database setup complete!")
        print("\nNext steps:")
        print("  1. Process images with OCR pipeline")
        print("  2. Results automatically saved to MongoDB")
        print("  3. Query results anytime\n")
    
    elif args.import_csv:
        print(f"\n📥 Importing from {args.import_csv}...")
        db.batch_import_csv(args.import_csv)
    
    elif args.export_csv:
        print(f"\n📤 Exporting to {args.export_csv}...")
        db.export_to_csv(args.export_csv)
    
    elif args.stats:
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        stats = db.get_statistics()
        print(f"Total images processed:    {stats['total_images']}")
        print(f"Successful detections:     {stats['successful_detections']}")
        print(f"Failed detections:         {stats['failed_detections']}")
        print(f"Unique wagon numbers:      {stats['unique_wagon_numbers']}")
        print(f"Average confidence:        {stats['average_confidence']:.1%}")
        print("="*60 + "\n")
    
    elif args.search:
        print(f"\n🔍 Searching for wagon number: {args.search}")
        results = db.search_by_wagon_number(args.search)
        
        if results:
            print(f"\nFound in {len(results)} images:")
            for r in results:
                print(f"  - {r['filename']} ({r['timestamp'].strftime('%Y-%m-%d %H:%M')})")
        else:
            print("No results found.")
    
    else:
        # Show recent results
        print(f"\n📊 Recent {args.recent} results:")
        print("="*60)
        results = db.get_recent_results(limit=args.recent)
        
        for r in results:
            wagon_nums = ', '.join(r['wagon_numbers']) if r['wagon_numbers'] else 'None'
            print(f"{r['filename']:30s} → {wagon_nums:20s} ({r['confidence']:.0%})")
        
        print("="*60 + "\n")
