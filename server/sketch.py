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
            
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply slight bilateral filtering to preserve edges while smoothing
        smooth = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance edges using adaptive thresholding
        edges = cv2.adaptiveThreshold(smooth, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        
        # Invert the grayscale image
        inverted = 255 - smooth
        
        # Apply Gaussian blur with adjusted parameters for better blending
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        
        # Invert the blurred image
        inverted_blurred = 255 - blurred
        
        # Dodge blend the images for a better pencil effect
        sketch_base = cv2.divide(smooth, inverted_blurred, scale=256.0)
        
        # Blend the sketch with edges for enhanced pencil lines
        sketch = cv2.addWeighted(sketch_base, 0.8, edges, 0.2, 0)
        
        # Optional: Add paper texture (subtle noise) for realism
        noise = np.random.normal(0, 2, sketch.shape).astype(np.uint8)
        sketch = cv2.add(sketch, noise)
        
        # Adjust contrast and brightness
        sketch = cv2.convertScaleAbs(sketch, alpha=1.05, beta=10)
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
            # Repeat the watermark in a grid pattern
            smaller_font_size = 40
            try:
                smaller_font = ImageFont.truetype("arial.ttf", smaller_font_size)
            except:
                smaller_font = font
                
            if hasattr(smaller_font, "getbbox"):
                bbox = smaller_font.getbbox(watermark_text)
                small_text_width = bbox[2] - bbox[0]
                small_text_height = bbox[3] - bbox[1]
            else:
                small_text_width, small_text_height = watermark_draw.textsize(watermark_text, font=smaller_font)
            
            # Create a diagonal grid pattern of watermarks
            grid_spacing = 300  # Space between watermarks
            angle = 30  # Angle for diagonal pattern
            margin = 20  # Define margin here to use in corner distance check
            
            for i in range(-2, int(img_width/grid_spacing) + 2):
                for j in range(-2, int(img_height/grid_spacing) + 2):
                    pos_x = i * grid_spacing
                    pos_y = j * grid_spacing + (i * grid_spacing * 0.5)  # Create diagonal offset
                    
                    # Skip if too close to bottom-right corner to avoid overlapping with main watermark
                    br_corner_distance = ((pos_x + small_text_width/2 - (img_width - margin))**2 + 
                                       (pos_y + small_text_height/2 - (img_height - margin))**2)**0.5
                    if br_corner_distance < 150:
                        continue
                        
                    # Add semi-transparent watermark text
                    watermark_draw.text((pos_x, pos_y), watermark_text, 
                                        font=smaller_font, fill=(255, 255, 255, 100))
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
            
        # Add watermark pattern across the image
        smaller_font_size = 40
        try:
            smaller_font = ImageFont.truetype("arial.ttf", smaller_font_size)
        except:
            smaller_font = font
            
        if hasattr(smaller_font, "getbbox"):
            bbox = smaller_font.getbbox(watermark_text)
            small_text_width = bbox[2] - bbox[0]
            small_text_height = bbox[3] - bbox[1]
        else:
            small_text_width, small_text_height = wm_draw.textsize(watermark_text, font=smaller_font)
            
        # Create pattern of watermarks across the image
        grid_spacing = 300
        for i in range(-1, int(img_width/grid_spacing) + 1):
            for j in range(-1, int(img_height/grid_spacing) + 1):
                pos_x = i * grid_spacing
                pos_y = j * grid_spacing + (i * grid_spacing * 0.5)
                
                # Skip if too close to center
                center_distance = ((pos_x - img_width/2)**2 + (pos_y - img_height/2)**2)**0.5
                if center_distance < 150:
                    continue
                    
                # Add semi-transparent watermarks
                wm_draw.text((pos_x, pos_y), watermark_text, font=smaller_font, fill=(255, 255, 255, 120))
                
        # Merge watermark with original image
        img = Image.alpha_composite(img.convert("RGBA"), watermark_layer).convert("RGB")
    except Exception as e:
        # If there's an error with the improved watermark, fall back to simple watermark
        print(f"Error adding enhanced watermark: {str(e)}")
        try:
            # Simple fallback watermark - large text with strong contrast
            draw = ImageDraw.Draw(img)
            draw.rectangle([
                (img_width//2 - 150, img_height//2 - 40),
                (img_width//2 + 150, img_height//2 + 40)
            ], fill=(0, 0, 0))
            draw.text(
                (img_width//2 - 100, img_height//2 - 30), 
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
