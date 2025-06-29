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
    
    # Apply professional-grade blur for natural transitions
    eye_region_mask = cv2.GaussianBlur(eye_region_mask, (0, 0), 
                                    sigmaX=width*0.01, sigmaY=height*0.01)
    
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
    
    # Add nose region emphasis - crucial for professional portraits
    nose_region_y_start = int(height * 0.45)
    nose_region_y_end = int(height * 0.55)
    nose_x_start = int(width * 0.4)
    nose_x_end = int(width * 0.6)
    
    nose_region_mask = np.zeros((height, width), dtype=np.float32)
    
    # Create subtle nose emphasis
    for y in range(nose_region_y_start, nose_region_y_end):
        for x in range(nose_x_start, nose_x_end):
            # Calculate normalized distance from nose center
            nose_center_y = (nose_region_y_start + nose_region_y_end) // 2
            nose_center_x = (nose_x_start + nose_x_end) // 2
            
            # Elliptical distance calculation
            normalized_x = (x - nose_center_x) / ((nose_x_end - nose_x_start) / 2)
            normalized_y = (y - nose_center_y) / ((nose_region_y_end - nose_region_y_start) / 2)
            dist = np.sqrt(normalized_x**2 + normalized_y**2)
            
            # Apply radial falloff with moderate emphasis
            if dist < 1.0:
                nose_region_mask[y, x] = 0.7 * (1.0 - dist)
    
    # Apply Gaussian blur for natural transitions
    nose_region_mask = cv2.GaussianBlur(nose_region_mask, (0, 0), 
                                    sigmaX=width*0.01, sigmaY=height*0.01)
    
    # Combine all feature masks
    feature_mask = np.maximum(eye_region_mask, mouth_region_mask)
    feature_mask = np.maximum(feature_mask, nose_region_mask)
    
    # Apply one final smooth blur for natural transitions
    feature_mask = cv2.GaussianBlur(feature_mask, (0, 0), sigmaX=width*0.01, sigmaY=height*0.01)
    
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
        sharpened = cv2.filter2D(smooth2, -1, kernel)
        
        # Combine smooth and sharp for more natural look
        base = cv2.addWeighted(smooth2, 0.7, sharpened, 0.3, 0)
        
        # Step 4: Create face region mask for enhanced facial features
        # Create enhanced face region mask with more natural falloff
        face_mask = np.zeros((height, width), dtype=np.float32)
        
        # Create a more natural oval/elliptical mask instead of rectangular
        center_x, center_y = width // 2, height // 2
        # Create elliptical gradient for more natural face region
        for y in range(height):
            for x in range(width):
                # Calculate normalized elliptical distance from center
                dist_x = abs(x - center_x) / (width * 0.4)
                dist_y = abs(y - center_y) / (height * 0.5)
                dist = np.sqrt(dist_x**2 + dist_y**2)
                
                # Apply radial falloff but emphasize face region
                if dist < 0.5:  # Central face area
                    face_mask[y, x] = max(0.65, 1.0 - dist*0.5)  # Increased minimum value
                elif dist < 1.0:  # Face periphery
                    face_mask[y, x] = max(0.35, 1.0 - dist*0.7)  # Increased minimum value
                else:  # Background
                    face_mask[y, x] = max(0, 1.0 - dist*0.9)
        
        # Apply Gaussian blur to smooth the mask transitions
        face_mask = cv2.GaussianBlur(face_mask, (0, 0), sigmaX=width*0.03, sigmaY=height*0.03)
        
        # Create professional feature mask for facial features
        feature_mask = create_professional_feature_mask(height, width, face_mask)
        
        # Step 5: Create the main sketch effect
        # Create inverted version for pencil effect
        inverted = 255 - base
        
        # Apply Gaussian blur for pencil-like effect
        blur = cv2.GaussianBlur(inverted, (0, 0), sigmaX=5, sigmaY=5)
        
        # Divide the grayscale image by the inverted-blurred image to create the pencil sketch effect
        sketch = cv2.divide(base, 255 - blur, scale=256)
        
        # Step 6: Enhance edges for clearer portrait features
        # Edge detection with different techniques to emphasize facial features
        edges1 = cv2.Laplacian(base, cv2.CV_8U, ksize=3)
        edges1 = cv2.threshold(edges1, 30, 255, cv2.THRESH_BINARY)[1]
        edges1 = cv2.GaussianBlur(edges1, (0, 0), sigmaX=1, sigmaY=1)
        
        # Apply Canny edge detection for finer edges
        edges2 = cv2.Canny(base, 50, 150)
        edges2 = cv2.dilate(edges2, None)
        edges2 = cv2.GaussianBlur(edges2, (0, 0), sigmaX=0.5, sigmaY=0.5)
        
        # Combine edges with the sketch
        sketch = cv2.addWeighted(sketch, 1.0, edges1, -0.15, 0)
        sketch = cv2.addWeighted(sketch, 1.0, edges2, -0.1, 0)
        
        # Step 7: Apply professional artistic effects for hand-drawn appearance
        # Apply adaptive thresholding for clearer lines - professional portrait technique
        adaptive = cv2.adaptiveThreshold(base, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
        adaptive = cv2.GaussianBlur(adaptive, (0, 0), sigmaX=1.5, sigmaY=1.5)
        
        # Blend in the adaptive threshold for stronger lines in key areas
        sketch = cv2.addWeighted(sketch, 0.8, adaptive, 0.2, 0)
        
        # Add realistic pencil texture
        np.random.seed(42)  # For reproducibility
        texture = np.random.normal(0, 3, sketch.shape).astype(np.uint8)
        sketch = cv2.add(sketch, texture)
        
        # Step 8: Apply final enhancements for professional-grade portrait
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
                draw.rectangle(
                    [(x - 10, y - 10), (x + text_width + 10, y + text_height + 10)], 
                    fill=(0, 0, 0, 128)
                )
                
                # Add the watermark text
                draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255))
                
                # Convert back to OpenCV format
                result = np.array(pil_img)
            except Exception as e:
                print(f"Error adding watermark: {str(e)}")
                # Continue without watermark if method fails
                result = np.array(pil_img)
        
        # Create a unique filename for the output
        output_filename = f"portrait_sketch_{uuid.uuid4().hex}.jpg"
        
        # Get the base directory of the script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(base_dir, "temp")
        output_path = os.path.join(temp_dir, output_filename)
        
        # Ensure the temp directory exists
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"Saving realistic portrait sketch to: {output_path}")
        # Save the sketch with high quality
        cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 99])
        
        return output_path
        
    except Exception as e:
        print(f"Error in realistic portrait sketch: {str(e)}")
        raise
