import os
import sys
import cv2
from PIL import Image
import numpy as np

# Import the sketch module
from sketch import convert_to_sketch

# Test with a sample image - let's look for any image in the server directory
server_dir = os.path.dirname(os.path.abspath(__file__))
image_files = []

# Look for jpg or png files in the server directory and its subdirectories
for root, dirs, files in os.walk(server_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(os.path.join(root, file))
            
if not image_files:
    print("No images found in server directory or its subdirectories.")
    sys.exit(1)
    
# Use the first found image
test_image_path = image_files[0]
print(f"Using test image: {test_image_path}")

# Convert the image with watermark
try:
    output_path = convert_to_sketch(test_image_path, add_watermark=True)
    print(f"Image processed and saved to: {output_path}")
    print("Watermark has been applied to the image in the bottom-right corner.")
    
    # Display the file path for manual verification
    print(f"Please check the image at: {output_path}")
except Exception as e:
    print(f"Error processing image: {str(e)}")
    sys.exit(1)
