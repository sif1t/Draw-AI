import os
import sys
import json
import uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path to import sketch module
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the sketch module
from sketch import add_watermark_to_base64_image
import base64

def create_test_image():
    """Create a test image similar to the cricket player sketch"""
    # Create directories
    upload_dir = os.path.join(current_dir, "uploads")
    temp_dir = os.path.join(current_dir, "temp")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create a simple image - 800x600 white background
    image = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add some lines to simulate a sketch
    for i in range(100):
        x1 = np.random.randint(0, 800)
        y1 = np.random.randint(0, 600)
        x2 = np.random.randint(0, 800)
        y2 = np.random.randint(0, 600)
        draw.line((x1, y1, x2, y2), fill=(200, 200, 200), width=1)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
        
    draw.text((300, 500), "Test Image", fill=(100, 100, 100), font=font)
    
    # Save the image
    input_path = os.path.join(upload_dir, "test_input.jpg")
    image.save(input_path)
    
    # Convert to sketch format (grayscale)
    sketch_image = image.convert('L')
    sketch_path = os.path.join(temp_dir, f"sketch_{uuid.uuid4().hex}.jpg")
    sketch_image.save(sketch_path)
    
    return input_path, sketch_path

def create_test_session(original_path, sketch_path):
    """Create a test session JSON file"""
    session_id = "test_session"
    temp_dir = os.path.join(current_dir, "temp")
    
    session_data = {
        "original_path": original_path,
        "sketch_path": sketch_path,
        "paid": False
    }
    
    session_file = os.path.join(temp_dir, f"{session_id}.json")
    with open(session_file, "w") as f:
        json.dump(session_data, f)
    
    return session_id

def add_watermark_to_image(image_path):
    """Add watermark to an image directly"""
    # Read image to base64
    with open(image_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Add watermark
    watermarked_base64 = add_watermark_to_base64_image(base64_image)
    
    # Decode and save
    img_data = base64.b64decode(watermarked_base64)
    watermarked_path = image_path.replace(".jpg", "_watermarked.jpg")
    with open(watermarked_path, "wb") as f:
        f.write(img_data)
    
    return watermarked_path

def main():
    # Create test image files
    original_path, sketch_path = create_test_image()
    print(f"Created test image: {original_path}")
    print(f"Created sketch: {sketch_path}")
    
    # Apply watermark directly to the sketch
    watermarked_path = add_watermark_to_image(sketch_path)
    print(f"Created watermarked image: {watermarked_path}")
    
    # Create test session
    session_id = create_test_session(original_path, sketch_path)
    print(f"Created test session: {session_id}")
    
    # API endpoints for testing
    base_url = "http://localhost:5000"
    free_download_url = f"{base_url}/api/download/free/{session_id}"
    normal_download_url = f"{base_url}/api/download/{session_id}"
    
    print("\nTest URLs:")
    print(f"Free download (with watermark): {free_download_url}")
    print(f"Normal download (depends on paid status): {normal_download_url}")

if __name__ == "__main__":
    main()
