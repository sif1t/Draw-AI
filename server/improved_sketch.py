import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import uuid
import io
import base64

def convert_to_pencil_sketch(image_path, add_watermark=True):
    """
    Convert an image to a high-quality artistic pencil sketch
    resembling professional hand-drawn portraits
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
                      Default is True for free version
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to professional pencil sketch. Add watermark: {add_watermark}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: Enhanced pre-processing for portrait-quality sketches
        # Resize if the image is too large (preserves quality and speeds up processing)
        max_dimension = 1200
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            
        # Convert to grayscale with enhanced portrait weights
        # Custom weights for portrait photography - emphasize facial details
        if len(img.shape) == 3:  # Color image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Enhance facial features
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        else:
            gray = img.copy()
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
        # Step 2: Structure enhancement - similar to pencil outlining in portraits
        # Bilateral filter to smooth while preserving edges (like pencil strokes)
        gray_smooth = cv2.bilateralFilter(gray, 15, 80, 80)
        
        # Step 3: Create dynamic range for realistic pencil effect
        # Adaptive histogram equalization for better local contrast
        gray_enhanced = clahe.apply(gray_smooth)
        
        # Step 4: Professional dodge and burn technique (similar to traditional drawing)
        # Invert the image
        inverted = 255 - gray_enhanced
        
        # Apply Gaussian blur with large kernel for broad shading
        blur_amount = int(min(height, width) * 0.03) | 1  # Must be odd number
        blur_amount = max(blur_amount, 7)  # Minimum 7 for good shading
        inverted_blur = cv2.GaussianBlur(inverted, (blur_amount, blur_amount), 0)
        
        # Apply professional dodge effect (simulates pencil pressure)
        pencil_sketch = cv2.divide(gray_smooth, 255 - inverted_blur, scale=256.0)
        
        # Step 5: Detail recovery (like fine pencil work)
        # Detect edges for detail enhancement
        edges = cv2.Laplacian(gray_smooth, cv2.CV_8U, ksize=3)
        edges = cv2.threshold(edges, 10, 255, cv2.THRESH_BINARY)[1]
        edges = 255 - edges  # Invert edges
        
        # Use a smaller blur for detailed edges (like fine pencil lines)
        detail_blur = cv2.GaussianBlur(edges, (3, 3), 0)
        
        # Step 6: Multi-layer blending (simulates layered pencil techniques)
        # Combine the dodge effect with recovered details
        sketch_details = cv2.addWeighted(pencil_sketch, 0.75, detail_blur, 0.25, 0)
        
        # Step 7: Tone adjustment for artistic finish
        # Further enhance contrast with a slight gamma correction
        gamma = 1.1
        sketch_gamma = np.array(255 * (sketch_details / 255) ** gamma, dtype=np.uint8)
        
        # Step 8: Artistic finishing touches
        # Apply a high-quality paper texture
        h, w = sketch_gamma.shape
        
        # Create a subtle textured paper background (like artist's paper)
        paper_texture = np.ones((h, w), dtype=np.uint8) * 248  # Very light gray
        
        # Add detailed paper grain
        np.random.seed(42)
        fine_grain = np.random.randint(245, 252, (h, w), dtype=np.uint8)  # Subtle grain
        medium_grain = np.random.randint(240, 250, (h//2, w//2), dtype=np.uint8)
        medium_grain = cv2.resize(medium_grain, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Combine grain layers
        paper_texture = cv2.addWeighted(paper_texture, 0.6, fine_grain, 0.3, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.8, medium_grain, 0.2, 0)
        
        # Merge sketch with paper texture using multiply blend
        result = cv2.multiply(sketch_gamma, paper_texture, scale=1/255.0)
        
        # Apply final contrast enhancement
        result = cv2.convertScaleAbs(result, alpha=1.05, beta=2)
    except Exception as e:
        print(f"Error in sketch conversion process: {str(e)}")
        raise
    
    # Add watermark if required
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(result)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark - use larger font size
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
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
            
            # Convert back to OpenCV format
            result = np.array(pil_img)
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Fallback watermark if the complex method fails
            try:
                # Simple text watermark as fallback
                draw.text((img_width - 150, img_height - 40), 
                      "DRAW AI", font=font, fill=(128, 128, 128))
                result = np.array(pil_img)
            except Exception as e2:
                print(f"Fallback watermark also failed: {str(e2)}")
                # Continue without watermark if all methods fail
                result = np.array(pil_img)
    
    # Create a unique filename for the output
    output_filename = f"sketch_{uuid.uuid4().hex}.jpg"
    
    # Get the base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "temp")
    output_path = os.path.join(temp_dir, output_filename)
    
    # Ensure the temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Saving sketch to: {output_path}")
    # Save the sketch
    cv2.imwrite(output_path, result)
    
    return output_path

def convert_to_realistic_pencil_sketch(image_path, add_watermark=True):
    """
    Convert an image to a detailed, realistic pencil sketch with
    professional shading and texture similar to artist drawings
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to detailed realistic pencil sketch. Add watermark: {add_watermark}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: Resize and optimize (helps with detail preservation)
        max_dimension = 1200
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            height, width = img.shape[:2]
        
        # Step 2: Advanced grayscale conversion with detail enhancement
        if len(img.shape) == 3:
            # Custom conversion with portrait-optimized weights
            b, g, r = cv2.split(img)
            gray = cv2.addWeighted(cv2.addWeighted(r, 0.4, g, 0.4, 0), 0.8, b, 0.2, 0)
        else:
            gray = img.copy()
            
        # Apply adaptive histogram equalization to enhance local details
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)
        
        # Step 3: Multi-level detail preservation
        # Bilateral filtering to preserve edges while smoothing (simulates pencil techniques)
        smooth1 = cv2.bilateralFilter(gray_enhanced, 5, 75, 75)  # Fine details
        smooth2 = cv2.bilateralFilter(gray_enhanced, 9, 150, 150)  # Medium details
        
        # Combine smoothed versions for natural pencil-like transitions
        smooth = cv2.addWeighted(smooth1, 0.6, smooth2, 0.4, 0)
        
        # Step 4: Advanced pencil shading simulation
        # Create dark regions first (simulates initial sketch outlines)
        inverted = 255 - smooth
        
        # Calculate adaptive kernel size based on image dimensions
        kernel_size = max(int(min(width, height) * 0.04) | 1, 11)
        if kernel_size % 2 == 0:
            kernel_size += 1  # Ensure odd kernel size
            
        # Make sure the second kernel size is also odd and at least 3
        kernel_size2 = max(kernel_size//2, 3)
        if kernel_size2 % 2 == 0:
            kernel_size2 += 1
            
        # Multi-radius blurring to simulate natural pencil shading gradations
        blur1 = cv2.GaussianBlur(inverted, (kernel_size, kernel_size), 0)  # Broad shading
        blur2 = cv2.GaussianBlur(inverted, (kernel_size2, kernel_size2), 0)  # Medium detail
        
        # Combine blur layers for natural pencil gradient effect
        inverted_blur = cv2.addWeighted(blur1, 0.7, blur2, 0.3, 0)
        
        # Step 5: Advanced pencil rendering with dodge blend
        # The division creates the realistic pencil effect
        sketch = cv2.divide(smooth, 255 - inverted_blur, scale=256.0)
        
        # Step 6: Detail enhancement for hair, eyes, etc. (fine pencil work)
        # Edge detection for fine details
        edges = cv2.Laplacian(smooth, cv2.CV_8U, ksize=5)
        # Only keep strong edges
        _, edges_thresh = cv2.threshold(edges, 20, 255, cv2.THRESH_BINARY_INV)
        edges_blur = cv2.GaussianBlur(edges_thresh, (3, 3), 0)
        
        # Blend in fine details
        sketch_detailed = cv2.addWeighted(sketch, 0.8, edges_blur, 0.2, 0)
        
        # Step 7: Artistic contrast adjustment (simulates pencil pressure variation)
        # Apply local contrast enhancement
        clahe_final = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        sketch_contrast = clahe_final.apply(sketch_detailed)
        
        # Fine-tune contrast
        sketch_contrast = cv2.convertScaleAbs(sketch_contrast, alpha=1.15, beta=5)
        
        # Step 8: Create high-quality paper texture
        h, w = sketch_contrast.shape
        
        # Base paper (slightly off-white like sketch paper)
        paper_texture = np.ones((h, w), dtype=np.uint8) * 250
        
        # Create basic grain for paper texture
        np.random.seed(42)
        grain = np.random.randint(235, 255, (h, w), dtype=np.uint8)
        
        # Create multi-layer texture similar to artist's sketch paper
        np.random.seed(42)
        fine_grain = np.random.randint(245, 252, (h, w), dtype=np.uint8)
        medium_grain = np.random.randint(242, 250, (h//2, w//2), dtype=np.uint8)
        medium_grain = cv2.resize(medium_grain, (w, h), interpolation=cv2.INTER_LINEAR)
        coarse_grain = np.random.randint(235, 248, (h//4, w//4), dtype=np.uint8)
        coarse_grain = cv2.resize(coarse_grain, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Blend grain layers
        paper_texture = cv2.addWeighted(paper_texture, 0.7, fine_grain, 0.3, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.8, medium_grain, 0.15, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.9, coarse_grain, 0.1, 0)
        
        # Apply texture using multiply blend mode
        result = cv2.multiply(sketch_contrast, paper_texture, scale=1/255.0)
        
        # Final touch - slight sharpening for crisp details
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        result = cv2.filter2D(result, -1, kernel)
        
    except Exception as e:
        print(f"Error in sketch conversion process: {str(e)}")
        raise
    
    # Add watermark if required (same as previous function)
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(result)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark - use larger font size
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
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
            
            # Convert back to OpenCV format
            result = np.array(pil_img)
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Continue without watermark if method fails
            result = np.array(pil_img)
    
    # Create a unique filename for the output
    output_filename = f"sketch_{uuid.uuid4().hex}.jpg"
    
    # Get the base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "temp")
    output_path = os.path.join(temp_dir, output_filename)
    
    # Ensure the temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Saving sketch to: {output_path}")
    # Save the sketch
    cv2.imwrite(output_path, result)
    
    return output_path

def convert_to_ultra_clear_sketch(image_path, add_watermark=True):
    """
    Convert an image to a professional portrait pencil sketch that closely mimics
    hand-drawn artwork like the reference image. This optimized version creates
    deep blacks in dark areas (especially hair), fine details in facial features,
    and realistic shading with proper contrast like a professional drawing.
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to professional portrait sketch. Add watermark: {add_watermark}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: High-resolution optimization for fine detail
        max_dimension = 2400  # Higher resolution for professional detail
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            height, width = img.shape[:2]
        
        # Step 2: Enhanced grayscale conversion for portraits
        if len(img.shape) == 3:
            # Custom channel mixing for portraits
            b, g, r = cv2.split(img)
            # Formula optimized for skin tones and hair detail
            gray = cv2.addWeighted(r, 0.5, g, 0.3, 0)
            gray = cv2.addWeighted(gray, 0.85, b, 0.15, 0)
        else:
            gray = img.copy()
        
        # Step 3: Enhance mid-tones with gamma correction
        gamma = 1.15
        gray_gamma = np.array(255 * (gray / 255) ** gamma, dtype='uint8')
        
        # Step 4: Enhance local contrast for facial features
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray_gamma)
        
        # Step 5: Create subtle paper texture
        h, w = gray_enhanced.shape
        paper_texture = np.ones((h, w), dtype=np.uint8) * 250
        
        # Add very subtle grain
        np.random.seed(42)
        fine_grain = np.random.randint(248, 255, (h, w), dtype=np.uint8)
        paper_texture = cv2.addWeighted(paper_texture, 0.85, fine_grain, 0.15, 0)
        
        # Step 6: Prepare base for professional sketch
        # Use bilateral filter to preserve edges while smoothing flat areas
        smooth = cv2.bilateralFilter(gray_enhanced, 9, 25, 35)
        
        # Step 7: Create dark strokes (for hair and strong features)
        # Deep shadows for realistic depth (like professional drawing)
        inverted = 255 - smooth
        
        # Large kernel for deep shadows (like in hair)
        kernel_deep = int(min(width, height) * 0.03) | 1  # Ensure odd number
        if kernel_deep % 2 == 0:
            kernel_deep += 1
        blur_deep = cv2.GaussianBlur(inverted, (kernel_deep, kernel_deep), 0)
        
        # Mid-sized kernel for medium tones
        kernel_mid = int(min(width, height) * 0.015) | 1  # Ensure odd number
        if kernel_mid % 2 == 0:
            kernel_mid += 1
        blur_mid = cv2.GaussianBlur(inverted, (kernel_mid, kernel_mid), 0)
        
        # Blend shadows with appropriate weights
        shadow_blend = cv2.addWeighted(blur_deep, 0.6, blur_mid, 0.4, 0)
        
        # Step 8: Create the base sketch with professional dodge blend
        sketch_base = cv2.divide(smooth, 255 - shadow_blend, scale=256.0)
        
        # Step 9: Enhance details in key areas (eyes, hair, facial features)
        # Extract edge details
        edges = cv2.Laplacian(smooth, cv2.CV_8U, ksize=3)
        _, edges_thresh = cv2.threshold(edges, 10, 255, cv2.THRESH_BINARY_INV)
        
        # Add detailed edges to the sketch
        sketch_enhanced = cv2.addWeighted(sketch_base, 0.75, edges_thresh, 0.25, 0)
        
        # Step 10: Apply targeted contrast enhancement
        # Enhance contrast while preserving mid-tone details
        sketch_contrast = cv2.convertScaleAbs(sketch_enhanced, alpha=1.3, beta=-10)
        
        # Step 11: Specifically enhance dark areas (especially for hair)
        # Create mask for dark areas
        _, dark_mask = cv2.threshold(inverted, 180, 255, cv2.THRESH_BINARY)
        dark_mask = cv2.GaussianBlur(dark_mask, (15, 15), 0)
        
        # Create darker version for hair and deep shadows
        sketch_dark = cv2.convertScaleAbs(sketch_contrast, alpha=1.5, beta=-20)
        
        # Blend normal and dark versions based on mask
        dark_ratio = dark_mask / 255.0
        sketch_final = sketch_contrast * (1.0 - dark_ratio) + sketch_dark * dark_ratio
        sketch_final = np.clip(sketch_final, 0, 255).astype(np.uint8)
        
        # Step 12: Sharpen details for professional finish
        sharpen_kernel = np.array([[-0.3, -0.3, -0.3], 
                                   [-0.3, 3.4, -0.3], 
                                   [-0.3, -0.3, -0.3]])
        sketch_sharp = cv2.filter2D(sketch_final, -1, sharpen_kernel)
        
        # Step 13: Merge with paper texture (like real pencil on paper)
        result = cv2.multiply(sketch_sharp, paper_texture, scale=1/255.0)
        
        # Final adjustment for professional finish
        result = cv2.convertScaleAbs(result, alpha=1.05, beta=2)
        
    except Exception as e:
        print(f"Error in ultra-clear sketch conversion: {str(e)}")
        raise
    
    # Add watermark if required
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(result)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark - use larger font size
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
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
            
            # Convert back to OpenCV format
            result = np.array(pil_img)
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Continue without watermark if method fails
            result = np.array(pil_img)
    
    # Create a unique filename for the output
    output_filename = f"sketch_{uuid.uuid4().hex}.jpg"
    
    # Get the base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "temp")
    output_path = os.path.join(temp_dir, output_filename)
    
    # Ensure the temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Saving ultra-clear sketch to: {output_path}")
    # Save the sketch with high quality
    cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 98])
    
    return output_path

def convert_to_base64(image_path):
    """
    Convert an image file to base64 encoding
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Base64 encoded string of the image
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Cannot convert to base64, file not found: {image_path}")
            
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error in base64 conversion: {str(e)}")
        raise
