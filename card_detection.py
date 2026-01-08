import cv2
import numpy as np


class CardDetector:
    """Detects and extracts ID cards from images."""
    
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
    
    def _show_image(self, window_name, image, max_width=1200, max_height=800):
        """Display image in a window with automatic resizing to fit screen."""
        if not self.debug_mode:
            return
            
        h, w = image.shape[:2]
        scale_width = max_width / w
        scale_height = max_height / h
        scale = min(scale_width, scale_height, 1.0)
        new_width = int(w * scale)
        new_height = int(h * scale)
        
        if scale < 1.0:
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            cv2.imshow(window_name, resized)
        else:
            cv2.imshow(window_name, image)
        
        # Wait for key press to continue
        print(f"  [DEBUG] Showing '{window_name}' - Press any key to continue...")
        cv2.waitKey(0)
    
    def _try_canny(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        edges = cv2.Canny(blurred, 30, 200)
        
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.contourArea(c) > 1000:
                return approx
        return None

    def detect_card(self, image_path):
        """Main function to detect ID card and return straightened card image."""
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Error: Could not load image from {image_path}")
            return {'success': False}
        
        print(f"✓ Loaded image: {image.shape[1]}x{image.shape[0]} pixels")
        original_with_detection = image.copy()
        
        # Strategy 1: Standard Canny on Original (Existing)
        card_contour = self._try_canny(image)
        
        # Strategy 2: Resize + Canny (if large image)
        if card_contour is None and image.shape[1] > 1000:
            print("⚠ Standard detection failed. Retrying with resizing...")
            ratio = 1000.0 / image.shape[1]
            dim = (1000, int(image.shape[0] * ratio))
            resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
            
            cnt = self._try_canny(resized)
            if cnt is not None:
                card_contour = (cnt / ratio).astype("int")
                print("✅ Found card using resizing!")

        # Strategy 3: Thresholding (Otsu)
        if card_contour is None:
            print("⚠ Edge detection failed. Retrying with thresholding...")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours on threshold
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            
            # Use fallback detection logic on these contours
            card_contour = self._fallback_detection(None, contours)
            if card_contour is not None:
                 print("✅ Found card using thresholding!")

        # If found, draw it
        if card_contour is not None:
             cv2.drawContours(original_with_detection, [card_contour], -1, (0, 255, 0), 3)
        else:
             print("❌ Could not detect a rectangular card")
             return {'success': False, 'original': image}

        if self.debug_mode:
            self._show_image('Detected Card', original_with_detection)
        
        # Apply perspective transform
        card_image = self._four_point_transform(image, card_contour.reshape(4, 2))
        print(f"✓ Card extracted: {card_image.shape[1]}x{card_image.shape[0]} pixels")
        
        # Show final extracted card in debug mode
        if self.debug_mode:
            self._show_image('Final Extracted Card', card_image)
            cv2.destroyAllWindows()  # Close all debug windows after showing final result
        
        return {
            'success': True,
            'card_image': card_image,
            'original': original_with_detection,
            'contour': card_contour
        }
    
    def _fallback_detection(self, edges, contours):
        """Fallback method with relaxed parameters."""
        print("⚠ Trying fallback detection with relaxed parameters...")
        for i, contour in enumerate(contours):
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
            
            if 4 <= len(approx) <= 6:
                area = cv2.contourArea(contour)
                if area > 5000:
                    print(f"✓ Found card with fallback (#{i}): {len(approx)} corners, area: {area:.0f}")
                    if len(approx) > 4:
                        rect = cv2.minAreaRect(contour)
                        box = cv2.boxPoints(rect)
                        approx = np.intp(box)
                    return approx
        return None
    
    def _order_points(self, pts):
        """Order points in: top-left, top-right, bottom-right, bottom-left."""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect
    
    def _four_point_transform(self, image, pts):
        """Apply perspective transformation."""
        rect = self._order_points(pts)
        (tl, tr, br, bl) = rect
        
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        warped = self._auto_rotate_card(warped)
        return warped
    
    def _auto_rotate_card(self, card_image):
        """Automatically rotate card to correct orientation."""
        height, width = card_image.shape[:2]
        
        if height > width:
            card_image = cv2.rotate(card_image, cv2.ROTATE_90_CLOCKWISE)
            height, width = card_image.shape[:2]
            print("  ↻ Rotated card to landscape orientation")
        
        orientations = [
            ('original', card_image),
            ('180°', cv2.rotate(card_image, cv2.ROTATE_180))
        ]
        
        best_score = -1
        best_orientation = card_image
        best_name = 'original'
        
        for name, oriented_img in orientations:
            score = self._calculate_text_score(oriented_img)
            if score > best_score:
                best_score = score
                best_orientation = oriented_img
                best_name = name
        
        if best_name != 'original':
            print(f"  ↻ Rotated card {best_name} for correct text orientation")
        
        return best_orientation
    
    def _calculate_text_score(self, image):
        """Calculate score for text orientation."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        height, width = edges.shape
        top_third = edges[0:height//3, :]
        middle_third = edges[height//3:2*height//3, :]
        top_edges = np.sum(top_third > 0)
        middle_edges = np.sum(middle_third > 0)
        score = (top_edges * 2.0) + (middle_edges * 1.0)
        return score