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

def convert_to_artistic_portrait_sketch(image_path, add_watermark=True):
    """
    Convert an image to a high-quality artistic portrait pencil sketch.
    This produces results similar to professional artist hand-drawn portraits
    with detailed shading and texture.
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to artistic portrait sketch. Add watermark: {add_watermark}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: Optimize image for portrait processing
        max_dimension = 1500  # Higher resolution for more detail
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            height, width = img.shape[:2]
        
        # Step 2: Professional portrait enhancement
        # Apply facial feature-aware processing
        if len(img.shape) == 3:
            # Professional portrait photographers use custom RGB channel mixing
            b, g, r = cv2.split(img)
            # Portrait-optimized weights (emphasizes skin tones and features)
            gray = cv2.addWeighted(cv2.addWeighted(r, 0.33, g, 0.33, 0), 0.7, b, 0.3, 0)
            
            # Enhance all details with adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        else:
            gray = img.copy()
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        
        # Step 3: Multi-level detail preservation (simulates artist's approach)
        # Artists first look at overall structure, then details
        # Preserve details at multiple levels using bilateral filtering
        detail_levels = []
        
        # Level 1: Fine details (eyes, eyelashes, fine hair, etc.)
        fine = cv2.bilateralFilter(gray, 5, 20, 50)
        detail_levels.append(fine)
        
        # Level 2: Medium details (facial features, hair strands)
        medium = cv2.bilateralFilter(gray, 7, 50, 100)
        detail_levels.append(medium)
        
        # Level 3: Large structures (overall face shape, major shadows)
        large = cv2.bilateralFilter(gray, 9, 100, 150)
        detail_levels.append(large)
        
        # Step 4: Edge detection at multiple levels (simulates pencil lines of varying pressure)
        edge_maps = []
        
        # Soft edges (light pencil touch)
        soft_edges = cv2.Laplacian(fine, cv2.CV_8U, ksize=3)
        _, soft_edges = cv2.threshold(soft_edges, 10, 255, cv2.THRESH_BINARY_INV)
        soft_edges = cv2.GaussianBlur(soft_edges, (3, 3), 0)
        edge_maps.append(soft_edges)
        
        # Medium edges (normal pencil pressure)
        med_edges = cv2.Laplacian(medium, cv2.CV_8U, ksize=5)
        _, med_edges = cv2.threshold(med_edges, 15, 255, cv2.THRESH_BINARY_INV)
        edge_maps.append(med_edges)
        
        # Strong edges (firm pencil pressure for outlines)
        strong_edges = cv2.Canny(large, 30, 100)
        strong_edges = 255 - strong_edges  # Invert for proper blending
        edge_maps.append(strong_edges)
        
        # Step 5: Advanced shading simulation (like an artist's cross-hatching technique)
        # Invert image for shading calculation
        inverted = 255 - fine
        
        # Create broad shading
        kernel_size_large = max(int(min(width, height) * 0.05) | 1, 21) 
        if kernel_size_large % 2 == 0:
            kernel_size_large += 1
        broad_shade = cv2.GaussianBlur(inverted, (kernel_size_large, kernel_size_large), 0)
        
        # Create medium shading
        kernel_size_medium = max(int(min(width, height) * 0.03) | 1, 11)
        if kernel_size_medium % 2 == 0:
            kernel_size_medium += 1
        medium_shade = cv2.GaussianBlur(inverted, (kernel_size_medium, kernel_size_medium), 0)
        
        # Create fine shading (detailed shadows)
        kernel_size_small = 5
        fine_shade = cv2.GaussianBlur(inverted, (kernel_size_small, kernel_size_small), 0)
        
        # Combine shading layers with emphasis on fine details
        combined_shade = cv2.addWeighted(
            cv2.addWeighted(broad_shade, 0.5, medium_shade, 0.5, 0),
            0.7, fine_shade, 0.3, 0
        )
        
        # Step 6: Dodge blend for base sketch (simulates the layering of pencil)
        sketch_base = cv2.divide(fine, 255 - combined_shade, scale=256.0)
        
        # Step 7: Professional blending of all elements (like an artist's integrated approach)
        # Start with base sketch
        artistic_blend = sketch_base.copy()
        
        # Add edge details sequentially (simulates layered drawing process)
        # Stronger edges need less opacity
        artistic_blend = cv2.addWeighted(artistic_blend, 0.7, edge_maps[0], 0.3, 0)
        artistic_blend = cv2.addWeighted(artistic_blend, 0.8, edge_maps[1], 0.2, 0)
        artistic_blend = cv2.addWeighted(artistic_blend, 0.9, edge_maps[2], 0.1, 0)
        
        # Step 8: Professional contrast enhancement for depth
        # Enhance contrast
        clahe_final = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        sketch_enhanced = clahe_final.apply(artistic_blend)
        
        # Further refine the drawing with local adjustments
        sketch_enhanced = cv2.convertScaleAbs(sketch_enhanced, alpha=1.2, beta=2)
        
        # Step 9: High-quality artist paper simulation
        h, w = sketch_enhanced.shape
        
        # Premium sketch paper texture (creamy off-white)
        paper_texture = np.ones((h, w), dtype=np.uint8) * 252
        
        # Multi-layered paper grain (simulates artist-grade paper)
        np.random.seed(42)
        fine_grain = np.random.randint(248, 255, (h, w), dtype=np.uint8)
        fine_grain = cv2.GaussianBlur(fine_grain, (3, 3), 0)
        
        # Medium grain (tooth of the paper)
        medium_grain_pattern = np.random.randint(245, 253, (h//3, w//3), dtype=np.uint8)
        medium_grain = cv2.resize(medium_grain_pattern, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Subtle large grain (paper manufacturing patterns)
        coarse_grain_pattern = np.random.randint(240, 250, (h//5, w//5), dtype=np.uint8)
        coarse_grain = cv2.resize(coarse_grain_pattern, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Blend grain layers like premium artist paper
        paper_texture = cv2.addWeighted(paper_texture, 0.8, fine_grain, 0.2, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.85, medium_grain, 0.15, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.9, coarse_grain, 0.1, 0)
        
        # Step 10: Final artistic integration
        # Blend sketch with premium paper texture
        result = cv2.multiply(sketch_enhanced, paper_texture, scale=1/255.0)
        
        # Final artistic enhancements - subtle sharpening for crisp details
        kernel = np.array([[-0.3, -0.3, -0.3], [-0.3, 3.4, -0.3], [-0.3, -0.3, -0.3]])
        result = cv2.filter2D(result, -1, kernel)
        
    except Exception as e:
        print(f"Error in artistic portrait sketch process: {str(e)}")
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
    
    print(f"Saving artistic portrait sketch to: {output_path}")
    # Save the sketch
    cv2.imwrite(output_path, result)
    
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
