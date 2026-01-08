import os
import cv2
import pytesseract
from pathlib import Path
from dotenv import load_dotenv

from card_detection import CardDetector
from field_filter import FieldExtractor
from text_extraction import TextExtractor

# Load environment variables
load_dotenv()

# Set Tesseract path if available
tesseract_path = os.getenv('TESSERACT_PATH')
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


class IDCardProcessor:
    """Main pipeline for processing ID cards."""
    
    def __init__(self, debug_mode=False):
        self.detector = CardDetector(debug_mode=debug_mode)
        self.field_extractor = FieldExtractor(debug_mode=debug_mode)
        self.text_extractor = TextExtractor(x_threshold=200, debug_mode=debug_mode)
    
    def process_image(self, image_path, output_dir='output', progress_callback=None):
        """Process a single ID card image through the entire pipeline."""
        print(f"\n{'='*70}")
        print(f"📷 Processing: {image_path}")
        print('='*70)
        
        # Get base name for output files
        base_name = Path(image_path).stem
        
        if progress_callback:
            progress_callback("detecting_card", 10)

        # Step 1: Detect and extract card
        print("\n[Step 1/3] Card Detection")
        print('-'*70)
        result = self.detector.detect_card(image_path)
        
        if not result['success']:
            print("❌ Failed to detect card")
            if progress_callback:
                progress_callback("failed_detection", 0)
            return None
        
        if progress_callback:
            progress_callback("extracting_fields", 40)

        # Save detected card
        os.makedirs(output_dir, exist_ok=True)
        card_path = os.path.join(output_dir, f'{base_name}_detected_card.jpg')
        cv2.imwrite(card_path, result['card_image'])
        print(f"✓ Saved detected card to: {card_path}")
        
        # Step 2: Extract fields
        print("\n[Step 2/3] Field Extraction")
        print('-'*70)
        field_info = self.field_extractor.extract_fields(
            result['card_image'], base_name, output_dir
        )
        
        if progress_callback:
            progress_callback("performing_ocr", 70)

        # Step 3: Extract text
        print("\n[Step 3/3] Text Extraction (OCR)")
        print('-'*70)
        extracted_texts = self.text_extractor.extract_text(
            field_info, base_name, output_dir
        )

        if progress_callback:
            progress_callback("completed", 100)
        
        print(f"\n{'='*70}")
        print("✅ SUCCESS! Processing complete")
        print('='*70)
        
        return {
            'image_path': image_path,
            'base_name': base_name,
            'card_image': result['card_image'],
            'extracted_texts': extracted_texts
        }
    
    def process_directory(self, input_dir='input_images', output_dir='output'):
        """Process all images in a directory."""
        print("="*70)
        print("ID CARD PROCESSING PIPELINE")
        print("="*70)
        
        # Find all image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        image_files = [
            f for f in os.listdir(input_dir)
            if f.lower().endswith(image_extensions) and os.path.isfile(os.path.join(input_dir, f))
        ]
        
        if not image_files:
            print(f"❌ No images found in '{input_dir}'")
            return []
        
        print(f"\n✓ Found {len(image_files)} images to process")
        
        results = []
        for i, image_file in enumerate(image_files, 1):
            image_path = os.path.join(input_dir, image_file)
            print(f"\n\n[Image {i}/{len(image_files)}]")
            
            result = self.process_image(image_path, output_dir)
            if result:
                results.append(result)
        
        # Print summary
        print("\n\n" + "="*70)
        print("PROCESSING SUMMARY")
        print("="*70)
        print(f"Total images processed: {len(image_files)}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {len(image_files) - len(results)}")
        
        for result in results:
            print(f"\n{result['base_name']}:")
            for item in result['extracted_texts']:
                text_val = item['text'] if isinstance(item, dict) else item
                print(f"  - {text_val}")        
        return results


def main():
    """Main entry point."""
    # Configuration
    INPUT_DIR = 'input_images'
    OUTPUT_DIR = 'output'
    DEBUG_MODE = False  # Set to True to see intermediate visualizations with key waits
    
    # Create processor
    processor = IDCardProcessor(debug_mode=DEBUG_MODE)
    
    # Process all images in directory
    processor.process_directory(INPUT_DIR, OUTPUT_DIR)
    
    print(f"\n✓ All results saved to '{OUTPUT_DIR}' directory")


if __name__ == "__main__":
    main()