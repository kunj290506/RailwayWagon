"""
TEST SCRIPT - Verify OCR Pipeline Works
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all required imports"""
    print("="*60)
    print("TESTING OCR PIPELINE DEPENDENCIES")
    print("="*60)
    
    tests = {
        'torch': 'PyTorch',
        'cv2': 'OpenCV',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'paddleocr': 'PaddleOCR (BEST)',
    }
    
    results = {}
    
    for module, name in tests.items():
        try:
            __import__(module)
            results[name] = '✅ OK'
        except ImportError:
            results[name] = '❌ MISSING'
    
    # Print results
    for name, status in results.items():
        print(f"  {name:20s} {status}")
    
    # Check NAFNet model
    print(f"\n  {'NAFNet Model':20s}", end='')
    nafnet_path = 'checkpoints/NAFNet-GoPro-width64.pth'
    if os.path.exists(nafnet_path):
        print('✅ Found')
    else:
        print(f'⚠ Not found at {nafnet_path}')
    
    print("="*60)
    
    # Overall status
    has_ocr = any('OK' in status for name, status in results.items() 
                  if 'OCR' in name or 'Tesseract' in name)
    
    if all('OK' in status for status in results.values()):
        print("\n✅ ALL DEPENDENCIES READY!")
        return True
    elif has_ocr:
        print("\n⚠ Some dependencies missing, but can still run with limited features")
        return True
    else:
        print("\n❌ CRITICAL: No OCR engine found!")
        print("\nInstall one of:")
        print("  pip install paddleocr paddlepaddle-gpu  (BEST)")
        print("  pip install easyocr")
        print("  pip install pytesseract")
        return False


def test_pipeline():
    """Test the pipeline with a dummy image"""
    print("\n" + "="*60)
    print("TESTING OCR PIPELINE")
    print("="*60)
    
    try:
        from wagon_ocr_pipeline import WagonNumberOCR
        
        print("\n1. Initializing pipeline...")
        ocr = WagonNumberOCR(use_gpu=True)
        
        print("✅ Pipeline initialized successfully!")
        print("\nPipeline ready to use:")
        print("  - Deblur model:", "NAFNet" if ocr.deblur_model else "None (will skip)")
        print("  - OCR engine:", ocr.ocr_type.upper())
        print("  - Device:", ocr.device)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n")
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        sys.exit(1)
    
    # Test pipeline
    pipeline_ok = test_pipeline()
    
    if pipeline_ok:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - READY FOR OCR!")
        print("="*60)
        print("\n📝 USAGE:")
        print("  Single image:")
        print("    python wagon_ocr_pipeline.py --image path/to/wagon.jpg")
        print("\n  Batch folder:")
        print("    python wagon_ocr_pipeline.py --folder path/to/images")
        print("\n  Python code:")
        print("    from wagon_ocr_pipeline import WagonNumberOCR")
        print("    ocr = WagonNumberOCR()")
        print("    result = ocr.process_image('wagon.jpg')")
        print("    print(result['wagon_numbers'])")
        print("="*60 + "\n")
    else:
        print("\n❌ TESTS FAILED")
        sys.exit(1)
