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
    # Read the image
    img = cv2.imread(image_path)
    
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
            font = ImageFont.load_default()
        
        # Add watermark text
        watermark_text = "Draw AI - FREE VERSION"
        img_width, img_height = pil_img.size
        
        # Calculate position (center of image)
        text_width, text_height = draw.textsize(watermark_text, font=font)
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
        
        # Add semi-transparent text
        draw.text((x, y), watermark_text, font=font, fill=(200, 200, 200))
        
        # Convert back to OpenCV format
        sketch = np.array(pil_img)
    
    # Create a unique filename for the output
    output_filename = f"sketch_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join("temp", output_filename)
    
    # Ensure the temp directory exists
    os.makedirs("temp", exist_ok=True)
    
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
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

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
    watermark_text = "Draw AI - FREE VERSION"
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
