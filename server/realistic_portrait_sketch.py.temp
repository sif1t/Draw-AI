import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import uuid

def create_professional_feature_mask(height, width, face_mask):
    """
    Creates a professional-quality feature mask for portrait sketches that emphasizes
    eyes, mouth, and other key facial features as a real artist would.
    
    Args:
        height: Image height
        width: Image width
        face_mask: Existing face mask
        
    Returns:
        Feature mask with properly emphasized facial areas
    """
    # Create eye regions with professional emphasis
    eye_region_y_start = int(height * 0.25)
    eye_region_y_end = int(height * 0.45)
    left_eye_x_start = int(width * 0.25)
    left_eye_x_end = int(width * 0.45)
    right_eye_x_start = int(width * 0.55)
    right_eye_x_end = int(width * 0.75)
    
    eye_region_mask = np.zeros((height, width), dtype=np.float32)
    
    # Create oval/elliptical eye regions for more natural emphasis
    for y in range(eye_region_y_start, eye_region_y_end):
        for x in range(left_eye_x_start, left_eye_x_end):
            # Calculate normalized distance from left eye center
            eye_center_y = (eye_region_y_start + eye_region_y_end) // 2
            eye_center_x = (left_eye_x_start + left_eye_x_end) // 2
            
            # Elliptical distance calculation
            normalized_x = (x - eye_center_x) / ((left_eye_x_end - left_eye_x_start) / 2)
            normalized_y = (y - eye_center_y) / ((eye_region_y_end - eye_region_y_start) / 2)
            dist = np.sqrt(normalized_x**2 + normalized_y**2)
            
            # Apply radial falloff with strong center emphasis
            if dist < 1.0:
                eye_region_mask[y, x] = max(eye_region_mask[y, x], 0.9 * (1.0 - dist))
    
    # Right eye with similar calculation
    for y in range(eye_region_y_start, eye_region_y_end):
        for x in range(right_eye_x_start, right_eye_x_end):
            # Calculate normalized distance from right eye center
            eye_center_y = (eye_region_y_start + eye_region_y_end) // 2
            eye_center_x = (right_eye_x_start + right_eye_x_end) // 2
            
            # Elliptical distance calculation
            normalized_x = (x - eye_center_x) / ((right_eye_x_end - right_eye_x_start) / 2)
            normalized_y = (y - eye_center_y) / ((eye_region_y_end - eye_region_y_start) / 2)
            dist = np.sqrt(normalized_x**2 + normalized_y**2)
            
            # Apply radial falloff with strong center emphasis
            if dist < 1.0:
                eye_region_mask[y, x] = max(eye_region_mask[y, x], 0.9 * (1.0 - dist))
    
    # Apply Gaussian blur for natural transitions
    eye_region_mask = cv2.GaussianBlur(eye_region_mask, (0, 0), 
                                      sigmaX=width*0.01, sigmaY=height*0.01)  # Tighter blur for precision
                     
    # Create more precise mouth region detection
    mouth_region_y_start = int(height * 0.55)
    mouth_region_y_end = int(height * 0.7)
    mouth_x_start = int(width * 0.3)
    mouth_x_end = int(width * 0.7)
    
    mouth_region_mask = np.zeros((height, width), dtype=np.float32)
    
    # Create elliptical mouth region for natural emphasis
    mouth_center_y = (mouth_region_y_start + mouth_region_y_end) // 2
    mouth_center_x = (mouth_x_start + mouth_x_end) // 2
    mouth_width = mouth_x_end - mouth_x_start
    mouth_height = mouth_region_y_end - mouth_region_y_start
    
    for y in range(mouth_region_y_start, mouth_region_y_end):
        for x in range(mouth_x_start, mouth_x_end):
            # Elliptical distance calculation
            normalized_x = (x - mouth_center_x) / (mouth_width / 2)
            normalized_y = (y - mouth_center_y) / (mouth_height / 2)
            dist = np.sqrt(normalized_x**2 + normalized_y**2 * 1.2)  # Slightly wider oval shape
            
            # Apply radial falloff with emphasis on the center
            if dist < 1.0:
                mouth_region_mask[y, x] = 0.85 * (1.0 - dist)
    
    # Apply Gaussian blur for natural transitions
    mouth_region_mask = cv2.GaussianBlur(mouth_region_mask, (0, 0), 
                                       sigmaX=width*0.015, sigmaY=height*0.015)
    
    # Combine face feature masks
    feature_mask = np.maximum(eye_region_mask, mouth_region_mask)
    return feature_mask

def convert_to_realistic_portrait_sketch(image_path, add_watermark=True):
    """
    Convert an image to a hyper-realistic pencil sketch that looks exactly
    like a real artist-drawn pencil portrait with proper facial feature emphasis,
    skin texture, and hair detail.
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
    
    Returns:
        Path to the generated realistic portrait sketch
    """
    print(f"Converting image to realistic artist-quality portrait sketch. Add watermark: {add_watermark}")
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: Enhanced high-resolution processing for portrait detail
        max_dimension = 2500  # Higher resolution for professional-quality detail
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        elif max(height, width) < 1500:  # If image is too small, upscale for better detailing
            scale_factor = 1500 / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        # Get new dimensions after resize
        height, width = img.shape[:2]
        
        # Step 2: Superior grayscale conversion for realistic skin tones
        if len(img.shape) == 3:
            # Split channels for portrait-specific mixing
            b, g, r = cv2.split(img)
            
            # Professional artist-grade weights for realistic portrait sketches
            # Enhanced skin tone reproduction with greater emphasis on red channel for warmth
            gray = cv2.addWeighted(r, 0.5, g, 0.35, 0)  # More emphasis on red for better skin tones
            gray = cv2.addWeighted(gray, 0.92, b, 0.08, 0)  # Less blue influence for more natural look
            
            # Apply advanced CLAHE for professional-quality contrast in facial features
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Apply refined contrast enhancement for professional look with rich blacks
            alpha = 1.1  # Increased contrast boost for clearer lines
            beta = -10   # Darker for deeper, richer pencil-like appearance
            gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        else:
            gray = img.copy()
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        
        # Step 3: Apply professional quality filtering for ideal sketch base
        # Apply multi-stage bilateral filtering for natural skin texture preservation
        smooth1 = cv2.bilateralFilter(gray, 11, 30, 30)  # Stronger smoothing for skin areas
        smooth2 = cv2.bilateralFilter(smooth1, 7, 20, 20)  # Intermediate smoothing
        
        # Apply sharpening for better defined edges
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharp = cv2.filter2D(smooth2, -1, kernel)
        
        # Step 4: Apply adaptive edge detection for professional-quality line work
        edge1 = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                    cv2.THRESH_BINARY, 9, 9)
        edge2 = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 9, 9)
        edge = cv2.addWeighted(edge1, 0.5, edge2, 0.5, 0)
        
        # Step 5: Use feature detection to emphasize important portrait areas
        # Create a mask to emphasize important facial features
        feature_mask = create_professional_feature_mask(height, width, None)
        
        # Convert mask to uint8 (0-255) range
        feature_mask_norm = (feature_mask * 255).astype(np.uint8)
        
        # Apply edge enhancement in facial feature areas
        # Use feature mask to refine edge details
        edges_enhanced = cv2.bitwise_and(edge, feature_mask_norm)
        edges_standard = cv2.bitwise_and(edge, 255 - feature_mask_norm)
        edge = cv2.addWeighted(edges_enhanced, 1.5, edges_standard, 0.5, 0)
        
        # Step 6: Create professional shadow effect by inverting and blurring
        inverted = 255 - edge
        blur_amount = int(width * 0.03)  # Proportional blur for better scaling
        if blur_amount % 2 == 0:  # Ensure odd kernel size
            blur_amount += 1
        shadow = cv2.GaussianBlur(inverted, (blur_amount, blur_amount), 0)
        
        # Step 7: Blend shadow and edge layers with dodge technique for realistic pencil effect
        def dodge(front, back):
            # Dynamic blend for more natural pencil look
            result = 255 - np.minimum(255, (255 - back) * 255 / np.maximum(front, 1))
            return result.astype(np.uint8)
        
        # Apply multi-layer dodge for realistic depth
        sketch1 = dodge(shadow, edge)
        
        # Step 8: Apply tonal enhancement to improve realistic appearance
        # Apply curve adjustments for realistic pencil tone mapping
        lut = np.zeros((1, 256), dtype=np.uint8)
        # Generate custom tone curve for pencil sketch effect
        for i in range(256):
            # Tone curve that mimics graphite pencil response
            lut[0, i] = min(255, int(1.5 * i ** 0.9)) if i < 100 else min(255, int(0.8 * i + 70))
        
        # Apply the custom tone curve
        sketch2 = cv2.LUT(sketch1, lut)
        
        # Step 9: Add natural pencil texture and variations
        # Create realistic pencil texture
        np.random.seed(42)  # For reproducibility
        texture = np.random.normal(0, 3, sketch2.shape).astype(np.uint8)  # Changed from int8 to uint8
        sketch = cv2.add(sketch2, texture)
        
        # Apply final contrast enhancement for professional finish
        alpha = 1.2  # Contrast control
        beta = -5    # Brightness control
        sketch = cv2.convertScaleAbs(sketch, alpha=alpha, beta=beta)
        
        # Apply final sharpening for crisp, clear professional look
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sketch = cv2.filter2D(sketch, -1, kernel)
        
        # Final CLAHE to enhance local contrast like professional portrait artists do
        clahe_final = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        sketch = clahe_final.apply(sketch)
        
        # Set result
        result = sketch
        
        # Add watermark if required
        if add_watermark:
            # Convert OpenCV image to PIL format for adding watermark
            pil_img = Image.fromarray(result)
            draw = ImageDraw.Draw(pil_img)
            
            # Set font for watermark
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                # If arial is not available, use default
                font = ImageFont.load_default()
                
            # Add watermark text
            watermark_text = "DRAW AI"
            img_width, img_height = pil_img.size
            
            # Calculate position (bottom-right corner)
            try:
                # For newer versions of Pillow
                if hasattr(font, "getbbox"):  
                    bbox = font.getbbox(watermark_text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:  
                    # Fallback to deprecated method for older Pillow versions
                    text_width, text_height = draw.textsize(watermark_text, font=font)
                    
                margin = 20  # Margin from the edge
                x = img_width - text_width - margin
                y = img_height - text_height - margin
                
                # Add a semi-transparent background for the watermark
                draw.rectangle([x - 10, y - 10, x + text_width + 10, y + text_height + 10], 
                               fill=(255, 255, 255, 128))
                
                # Add text
                draw.text((x, y), watermark_text, fill=(80, 80, 80), font=font)
                
                # Convert back to OpenCV format
                result = np.array(pil_img)
            except Exception as e:
                print(f"Error adding watermark: {e}")
        
        # Save the result with unique filename
        output_dir = os.path.join(os.path.dirname(os.path.dirname(image_path)), "portrait_results")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        unique_id = uuid.uuid4().hex[:8]
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_realistic_portrait_{unique_id}.jpg")
        
        # Save with high quality
        cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        print(f"Realistic portrait sketch saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error in converting to realistic portrait sketch: {e}")
        raise
