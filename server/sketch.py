import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import uuid
import io
import base64

def convert_to_sketch(image_path, add_watermark=True):
    """
    Convert an image to a realistic pencil sketch
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
                      Default is True for free version
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to sketch. Add watermark: {add_watermark}")
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
            
        # Step 1: Enhanced grayscale conversion with art-focused processing
        if len(img.shape) == 3 and img.shape[2] == 3:
            # Extract individual color channels
            b, g, r = cv2.split(img)
            # Art-focused weighted grayscale that preserves portrait details
            gray = cv2.addWeighted(cv2.addWeighted(r, 0.4, g, 0.4, 0), 0.8, b, 0.2, 0)
            # Apply contrast stretching for better dynamic range
            p2, p98 = np.percentile(gray, (2, 98))
            gray = np.clip((gray - p2) * (255.0 / (p98 - p2 + 0.001)), 0, 255).astype(np.uint8)
        else:
            gray = img.copy()
            # Still apply contrast stretching for non-color images
            p2, p98 = np.percentile(gray, (2, 98))
            gray = np.clip((gray - p2) * (255.0 / (p98 - p2 + 0.001)), 0, 255).astype(np.uint8)
        
        # Step 2: Multi-stage detail preservation with artistic enhancement
        # Fine detail preservation with controlled bilateral filter
        smooth1 = cv2.bilateralFilter(gray, 3, 10, 10)  # Preserve finest details
        smooth2 = cv2.bilateralFilter(gray, 5, 30, 30)  # Mid-level details
        smooth3 = cv2.bilateralFilter(gray, 7, 50, 50)  # Broader areas
        
        # Combine smoothed versions with emphasis on fine details for realistic pencil look
        smooth = cv2.addWeighted(smooth1, 0.5, cv2.addWeighted(smooth2, 0.7, smooth3, 0.3, 0), 0.5, 0)
        
        # Step 3: Advanced multi-scale edge detection for artistic pencil stroke simulation
        # Ultra-fine details (hairlines, eyelashes, etc.)
        ultrafine_edges = cv2.adaptiveThreshold(smooth, 255, 
                                              cv2.ADAPTIVE_THRESH_MEAN_C, 
                                              cv2.THRESH_BINARY, 5, 1)
        
        # Fine details (facial features, thin lines)
        fine_edges = cv2.adaptiveThreshold(smooth, 255, 
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 7, 2)
        
        # Medium details (general contours)
        med_edges = cv2.adaptiveThreshold(smooth, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        
        # Create realistic pencil line weight variation by combining all edge scales
        edges = cv2.addWeighted(
            ultrafine_edges, 0.3, 
            cv2.addWeighted(fine_edges, 0.5, med_edges, 0.5, 0), 
            0.7, 0
        )
        
        # Step 4: Advanced pencil shading simulation 
        # Create detailed inverted layer with enhanced contrast
        inverted = 255 - smooth
        inverted = cv2.convertScaleAbs(inverted, alpha=1.1, beta=0)
        
        # Multi-radius blurring to simulate the natural gradation of pencil shading
        blur1 = cv2.GaussianBlur(inverted, (21, 21), 0)  # Broad shading
        blur2 = cv2.GaussianBlur(inverted, (11, 11), 0)  # Medium detail shading
        blur3 = cv2.GaussianBlur(inverted, (3, 3), 0)    # Fine detail shading
        
        # Weighted blending of blur layers for realistic pencil gradient effects
        blurred = cv2.addWeighted(
            blur1, 0.5, 
            cv2.addWeighted(blur2, 0.7, blur3, 0.3, 0),
            0.5, 0
        )
        
        # Invert blurred image with enhanced contrast
        inverted_blurred = cv2.convertScaleAbs(255 - blurred, alpha=1.05, beta=0)
        
        # Step 5: Advanced dodging for realistic pencil shading effects
        # Enhanced dodge blending that preserves dark areas like a real pencil sketch
        sketch_base = np.clip(255.0 * smooth / (inverted_blurred + 15), 0, 255).astype(np.uint8)
        
        # Apply a soft mask to enhance contrast in mid-tones
        gray_normalized = gray / 255.0
        contrast_mask = np.clip(4 * (gray_normalized - 0.5) * (gray_normalized - 0.5), 0, 1)
        contrast_enhanced = sketch_base * (1 - contrast_mask * 0.3)
        sketch_base = np.clip(contrast_enhanced, 0, 255).astype(np.uint8)
        
        # Step 6: Multi-layer blending for professional artist-quality pencil effect
        # Extract natural line detail using Laplacian edge detection
        detail_edges = cv2.Laplacian(smooth, cv2.CV_8U, ksize=3)
        # Apply threshold to create defined pencil lines
        detail_edges = cv2.threshold(detail_edges, 3, 255, cv2.THRESH_BINARY)[1]
        # Soften lines slightly for natural pencil look
        detail_edges = cv2.GaussianBlur(detail_edges, (3, 3), 0.5)
        
        # Blend all components with precise weights for realistic hand-drawn appearance
        # Base layer: shading and tones (like pencil pressure variations)
        # Edge layer: defined outlines (like deliberate pencil strokes)
        # Detail layer: fine details (like finishing touches)
        sketch_temp = cv2.addWeighted(sketch_base, 0.6, edges, 0.3, 0)
        sketch = cv2.addWeighted(sketch_temp, 0.85, detail_edges, 0.15, 0)
        
        # Step 7: Artistic paper texture simulation
        # Generate high-quality paper texture with subtle variations
        h, w = sketch.shape
        np.random.seed(42)  # For consistent texture
        # Create realistic paper grain pattern
        fine_texture = np.random.randint(0, 2, (h, w), dtype=np.int8)  # Very subtle grain
        
        # Apply texture with artistic control
        sketch_float = sketch.astype(float)
        
        # Only apply texture to mid-tones - protect highlights and shadows
        # Real pencil drawings have texture most visible in middle gray areas
        midtone_mask = 1.0 - np.abs(sketch_float - 128) / 128
        midtone_mask = midtone_mask * midtone_mask * 0.5  # Squared for smoother falloff
        sketch_float = sketch_float + fine_texture * midtone_mask
        sketch = np.clip(sketch_float, 0, 255).astype(np.uint8)
        
        # Step 8: Artistic finishing touches
        # Apply adaptive contrast enhancement with protection for highlights
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        sketch_enhanced = clahe.apply(sketch)
        
        # Preserve natural highlights
        highlight_mask = (sketch > 200).astype(np.uint8) * 255
        highlight_mask = cv2.GaussianBlur(highlight_mask, (5, 5), 0)
        highlight_mask = highlight_mask / 255.0
        
        # Blend enhanced contrast with original to protect highlights
        sketch = sketch_enhanced * (1 - highlight_mask) + sketch * highlight_mask
        
        # Apply natural pencil-like edge enhancement
        kernel = np.array([[-0.5,-0.5,-0.5], [-0.5,5,-0.5], [-0.5,-0.5,-0.5]]) / 1.5  # Gentler sharpening
        sketch = cv2.filter2D(sketch, -1, kernel)
        
        # Final delicate tone adjustment to match hand-drawn quality
        sketch = cv2.convertScaleAbs(sketch, alpha=1.02, beta=2)
    except Exception as e:
        print(f"Error in sketch conversion process: {str(e)}")
        raise
    
    # Add watermark if required
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(sketch)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark - use larger font size
        try:
            font = ImageFont.truetype("arial.ttf", 60)  # Increased font size
        except:
            # If arial is not available, use default
            font = ImageFont.load_default()
            
        # Add watermark text
        watermark_text = "DRAW AI"  # Using uppercase for better visibility
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
            
            # Create a new transparent layer for the watermark
            watermark_layer = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
            watermark_draw = ImageDraw.Draw(watermark_layer)
            
            # Add a large watermark in the bottom-right corner
            padding = 20
            watermark_bg_coords = [
                (x - padding, y - padding),
                (x + text_width + padding, y + text_height + padding)
            ]
            # Dark background rectangle for the main watermark
            watermark_draw.rectangle(watermark_bg_coords, fill=(0, 0, 0, 180))
            
            # Add the watermark text in white
            watermark_draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))
            
            # Add a watermark pattern across the entire image
            # No grid pattern of watermarks - only the main one in the bottom right corner
            margin = 20  # Define margin for positioning
            # Convert PIL RGBA to RGB and merge with original sketch
            pil_img = pil_img.convert("RGB")
            watermarked_img = Image.alpha_composite(
                pil_img.convert("RGBA"),
                watermark_layer
            ).convert("RGB")
            
            # Convert back to OpenCV format
            sketch = np.array(watermarked_img)
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Fallback watermark if the complex method fails
            try:
                # Simple text watermark as fallback (bottom-right corner)
                draw = ImageDraw.Draw(pil_img)
                margin = 20  # Margin from the edge
                draw.text((img_width - 200 - margin, img_height - 60 - margin), 
                          "DRAW AI", font=font, fill=(255, 255, 255))
                sketch = np.array(pil_img)
            except Exception as e2:
                print(f"Fallback watermark also failed: {str(e2)}")
                # Continue without watermark if all methods fail
                sketch = np.array(pil_img)
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
    cv2.imwrite(output_path, sketch)
    
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

def add_watermark_to_base64_image(base64_string):
    """
    Add watermark to an image represented as base64 string
    
    Args:
        base64_string: Base64 encoded image
    
    Returns:
        Base64 encoded image with watermark
    """
    # Decode the base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))
    
    # Create a drawing object
    draw = ImageDraw.Draw(img)
    
    # Set font for watermark - use larger font size
    try:
        font = ImageFont.truetype("arial.ttf", 60)  # Increased font size
    except:
        # If arial is not available, use default
        font = ImageFont.load_default()
      
    # Add watermark text
    watermark_text = "DRAW AI"  # Using uppercase for better visibility
    img_width, img_height = img.size
    
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
        
        # Create a watermark layer for the base64 image
        watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        wm_draw = ImageDraw.Draw(watermark_layer)
            
        # Add main large watermark in the bottom-right corner
        padding = 20
        watermark_bg_coords = [
            (x - padding, y - padding),
            (x + text_width + padding, y + text_height + padding)
        ]
        # Dark background for high visibility
        wm_draw.rectangle(watermark_bg_coords, fill=(0, 0, 0, 200))
            
        # Add the watermark text in bright white
        wm_draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 255))
            
        # No grid pattern of watermarks - only the main one in bottom-right corner
                
        # Merge watermark with original image
        img = Image.alpha_composite(img.convert("RGBA"), watermark_layer).convert("RGB")
    except Exception as e:
        # If there's an error with the improved watermark, fall back to simple watermark
        print(f"Error adding enhanced watermark: {str(e)}")
        try:
            # Simple fallback watermark in bottom-right corner
            draw = ImageDraw.Draw(img)
            margin = 30
            draw.rectangle([
                (img_width - 200 - margin, img_height - 60 - margin),
                (img_width - margin, img_height - margin)
            ], fill=(0, 0, 0))
            draw.text(
                (img_width - 180 - margin, img_height - 45 - margin), 
                "DRAW AI", 
                font=font, 
                fill=(255, 255, 255)
            )
        except Exception as e2:
            print(f"Even simple watermark failed: {str(e2)}")
    
    # Convert back to base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
