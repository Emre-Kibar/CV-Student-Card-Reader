import os
import cv2


class FieldExtractor:
    """Extracts text fields from ID cards."""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
    
    def _show_debug_image(self, window_name, image):
        """Show debug image if debug mode is enabled."""
        if not self.debug_mode:
            return
        
        print(f"  [DEBUG] Showing '{window_name}' - Press any key to continue...")
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
    
    def extract_fields(self, card_image, base_name, output_dir='output'):
        """Extract text fields from card image."""
        fields_dir = os.path.join(output_dir, f'{base_name}_fields')
        os.makedirs(fields_dir, exist_ok=True)
        
        original_image = card_image.copy()
        
        # Convert to grayscale and threshold
        gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
        self._show_debug_image('Field Extraction - Grayscale', gray)
        
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        self._show_debug_image('Field Extraction - Threshold', thresh)
        
        height, width = thresh.shape[:2]
        
        # Mask out non-text regions
        masks = [
            (int(width*0.01), int(height*0.01), int(width*0.12), int(height*0.99)),
            (int(width*0.01), int(height*0.00001), int(width*0.35), int(height*0.2)),
            (int(width*0.65), int(height*0.4), int(width*0.99), int(height*0.99))
        ]
        
        for x_start, y_start, x_end, y_end in masks:
            cv2.rectangle(thresh, (x_start, y_start), (x_end, y_end), (0), thickness=cv2.FILLED)
        
        self._show_debug_image('Field Extraction - After Masking', thresh)
        
        # Dilate to connect characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 4))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        self._show_debug_image('Field Extraction - Dilated', dilated)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print(f"✓ Found {len(contours)} potential text fields")
        
        field_info = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            if w > 30 and h > 10:
                cv2.rectangle(original_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                padding = 5
                field_crop = card_image[max(0, y - padding):min(y + h + padding, card_image.shape[0]),
                                       max(0, x - padding):min(x + w + padding, card_image.shape[1])]
                
                filename = f"{x}_{y}.jpg"
                field_path = os.path.join(fields_dir, filename)
                cv2.imwrite(field_path, field_crop)
                field_info.append({'x': x, 'y': y, 'path': field_path})
        
        # Save annotated image
        annotated_path = os.path.join(output_dir, f'{base_name}_annotated.jpg')
        cv2.imwrite(annotated_path, original_image)
        
        # Show final annotated image in debug mode
        if self.debug_mode:
            self._show_debug_image('Field Extraction - Detected Fields', original_image)
            cv2.destroyAllWindows()  # Close all debug windows
        
        print(f"✓ Saved {len(field_info)} field crops to '{fields_dir}'")
        return field_info