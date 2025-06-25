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
    
    Returns:
        Path to the generated sketch image
    """
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
        
        # Invert the grayscale image
        inverted = 255 - gray
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
        
        # Invert the blurred image
        inverted_blurred = 255 - blurred
        
        # Create the pencil sketch image
        sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
    except Exception as e:
        print(f"Error in sketch conversion process: {str(e)}")
        raise
    
    # Add watermark if required
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(sketch)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            # If arial is not available, use default
            font = ImageFont.load_default()        # Add watermark text
        watermark_text = "Draw AI - www.drawai.com"
        img_width, img_height = pil_img.size
        
        # Calculate position (center of image)
        try:
            # For newer versions of Pillow
            if hasattr(font, "getbbox"):  
                bbox = font.getbbox(watermark_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:  
                # Fallback to deprecated method for older Pillow versions
                text_width, text_height = draw.textsize(watermark_text, font=font)
                
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
            
            # Add semi-transparent text
            draw.text((x, y), watermark_text, font=font, fill=(200, 200, 200))
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Continue without watermark if there's an error
        
        # Convert back to OpenCV format
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
    
    # Set font for watermark
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        # If arial is not available, use default
        font = ImageFont.load_default()
      # Add watermark text
    watermark_text = "Draw AI - www.drawai.com"
    img_width, img_height = img.size
    
    # Calculate position (center of image)
    text_width, text_height = draw.textsize(watermark_text, font=font)
    x = (img_width - text_width) // 2
    y = (img_height - text_height) // 2
    
    # Add semi-transparent text
    draw.text((x, y), watermark_text, font=font, fill=(200, 200, 200))
    
    # Convert back to base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
