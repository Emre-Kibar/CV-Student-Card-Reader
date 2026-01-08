import os
import cv2
import pytesseract


class TextExtractor:
    """Extracts text from field images using OCR."""
    
    def __init__(self, x_threshold=200, debug_mode=False):
        self.x_threshold = x_threshold
        self.debug_mode = debug_mode
    
    def _show_debug_image(self, window_name, image):
        """Show debug image if debug mode is enabled."""
        if not self.debug_mode:
            return
        
        print(f"  [DEBUG] Showing '{window_name}' - Press any key to continue...")
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
    
    def extract_text(self, field_info, base_name, output_dir='output'):
        """Run OCR on field images and extract text."""
        # Filter fields by x coordinate
        filtered_fields = [f for f in field_info if f['x'] > self.x_threshold]
        print(f"✓ Processing {len(filtered_fields)} fields (x > {self.x_threshold})")
        
        # Sort by y coordinate (top to bottom)
        filtered_fields.sort(key=lambda f: f['y'])
        
        extracted_texts = []
        try:
            for i, field in enumerate(filtered_fields, 1):
                image = cv2.imread(field['path'])
                if image is None:
                    print(f"⚠ Warning: Could not read {field['path']}")
                    continue
                
                # Show field being processed in debug mode
                if self.debug_mode:
                    self._show_debug_image(f'OCR - Field {i}/{len(filtered_fields)}', image)
                
                config = '--psm 7'
                text = pytesseract.image_to_string(image, lang='tur', config=config)
                text = text.strip()
                
                if text:
                    print(f"  ✓ {os.path.basename(field['path'])} (y={field['y']}) -> {text}")
                    extracted_texts.append(text)
                else:
                    print(f"  ⚠ {os.path.basename(field['path'])} (y={field['y']}) -> No text")
            
            # Close all debug windows after OCR
            if self.debug_mode:
                cv2.destroyAllWindows()
        
        except pytesseract.TesseractNotFoundError:
            print("\n❌ TESSERACT NOT FOUND ERROR")
            print("Please install Tesseract-OCR and Turkish language pack")
            return []
        except Exception as e:
            print(f"❌ OCR error: {e}")
            return []
        
        # Save results
        output_file = os.path.join(output_dir, f'{base_name}_ocr_results.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            for text in extracted_texts:
                f.write(text + '\n')
        
        print(f"✓ Saved OCR results to '{output_file}'")
        return extracted_texts