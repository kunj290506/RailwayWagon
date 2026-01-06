"""
Dual-Mode OCR CLI - Wagon vs Normal Mode
Quick command-line interface for testing both modes
"""
from wagon_ocr_pipeline import WagonNumberOCR

def demo_wagon_mode(image_path):
    """Demo wagon mode - 11-digit rule"""
    print("\n" + "="*70)
    print("WAGON MODE - 11-Digit Wagon Number Detection")
    print("="*70)
    print("Rule: 2-4 letters + 7-9 digits = 11 total characters")
    print("Example: ABC12345678 (3 letters + 8 digits = 11)")
    print("="*70)
    
    ocr = WagonNumberOCR(use_gpu=True, mode='wagon')
    result = ocr.process_image(image_path)
    
    print(f"\nImage: {image_path}")
    print(f"Detected Wagon Numbers: {result['wagon_numbers']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"All Text Detected: {result['all_text']}")
    print("="*70 + "\n")
    
    return result


def demo_normal_mode(image_path):
    """Demo normal mode - all meaningful text"""
    print("\n" + "="*70)
    print("NORMAL MODE - All Meaningful Text Detection")
    print("="*70)
    print("Rule: Any text with 3+ characters")
    print("Example: ABC, 123, WAGON, TEXT456, etc.")
    print("="*70)
    
    ocr = WagonNumberOCR(use_gpu=True, mode='normal')
    result = ocr.process_image(image_path)
    
    print(f"\nImage: {image_path}")
    print(f"Detected Text: {result['wagon_numbers']}")  # All text, not just wagon numbers
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"All Text Detected: {result['all_text']}")
    print("="*70 + "\n")
    
    return result


def compare_modes(image_path):
    """Compare wagon vs normal mode side by side"""
    print("\n" + "="*70)
    print("COMPARING WAGON MODE vs NORMAL MODE")
    print("="*70)
    
    # Wagon mode
    print("\n[1] WAGON MODE (11-digit rule):")
    ocr_wagon = WagonNumberOCR(use_gpu=True, mode='wagon')
    result_wagon = ocr_wagon.process_image(image_path)
    print(f"    Found: {result_wagon['wagon_numbers']}")
    
    # Normal mode
    print("\n[2] NORMAL MODE (all meaningful text):")
    ocr_normal = WagonNumberOCR(use_gpu=True, mode='normal')
    result_normal = ocr_normal.process_image(image_path)
    print(f"    Found: {result_normal['wagon_numbers']}")
    
    print("\n" + "="*70)
    print("COMPARISON:")
    print(f"  Wagon Mode found:  {len(result_wagon['wagon_numbers'])} items (strict 11-digit)")
    print(f"  Normal Mode found: {len(result_normal['wagon_numbers'])} items (all text)")
    print("="*70 + "\n")
    
    return result_wagon, result_normal


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dual-Mode OCR Demo')
    parser.add_argument('image', type=str, help='Image path')
    parser.add_argument('--mode', type=str, choices=['wagon', 'normal', 'compare'], 
                       default='compare', help='OCR mode')
    
    args = parser.parse_args()
    
    if args.mode == 'wagon':
        demo_wagon_mode(args.image)
    elif args.mode == 'normal':
        demo_normal_mode(args.image)
    else:
        compare_modes(args.image)
