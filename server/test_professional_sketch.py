import os
import sys
import cv2
import numpy as np
from PIL import Image

# Import the sketch module
from sketch import convert_to_sketch

# Find any image in the server directory
server_dir = os.path.dirname(os.path.abspath(__file__))
image_files = []

# Look for jpg or png files in the server directory and its subdirectories
for root, dirs, files in os.walk(server_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and 'watermark' not in file.lower():
            image_files.append(os.path.join(root, file))
            
if not image_files:
    print("No images found in server directory or its subdirectories.")
    sys.exit(1)
    
# Use the first found image
test_image_path = image_files[0]
print(f"Using test image: {test_image_path}")

# Convert the image to a professional-quality pencil sketch
try:
    # Convert with watermark set to False to see the pure sketch effect
    output_path = convert_to_sketch(test_image_path, add_watermark=False)
    print(f"Professional-quality pencil sketch saved to: {output_path}")
    
    # Display the file path for manual verification
    print(f"\nPlease check the enhanced professional pencil sketch at: {output_path}")
    print("The image should now have:")
    print("- Detailed line work similar to hand-drawn sketches")
    print("- Nuanced shading with multiple tonal values")
    print("- Subtle paper texture for authenticity")
    print("- Professional-level contrast and detail preservation")
except Exception as e:
    print(f"Error processing image: {str(e)}")
    sys.exit(1)
