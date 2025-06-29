import os
import sys
import cv2
import numpy as np
from PIL import Image
import uuid

# Add the server directory to the path
server_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(server_dir)

# Import the realistic portrait sketch module
from realistic_portrait_sketch import convert_to_realistic_portrait_sketch

def test_realistic_portrait_sketch():
    """
    Test the realistic portrait sketch function on various images.
    This function will process portrait images and save the results for review.
    """
    print("Testing Realistic Portrait Sketch output...")
    
    # Create output directory
    output_dir = os.path.join(server_dir, "portrait_sketch_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Find portrait test images in the uploads folder
    uploads_dir = os.path.join(server_dir, "uploads")
    
    # Test on all images in the uploads directory
    test_count = 0
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            test_count += 1
            image_path = os.path.join(uploads_dir, filename)
            print(f"Processing image: {filename}")
            
            try:
                # Convert the image to a realistic portrait sketch
                sketch_path = convert_to_realistic_portrait_sketch(image_path, add_watermark=False)
                
                # Create a more descriptive output filename
                output_filename = f"realistic_portrait_{os.path.splitext(filename)[0]}_{uuid.uuid4().hex[:8]}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                
                # Copy the result to our test output directory
                sketch_img = cv2.imread(sketch_path)
                cv2.imwrite(output_path, sketch_img)
                
                print(f"  -> Saved result to: {output_path}")
            except Exception as e:
                print(f"  -> Error processing {filename}: {str(e)}")
    
    if test_count == 0:
        print("No test images found in the uploads directory.")
    else:
        print(f"Completed testing on {test_count} images.")
        print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    test_realistic_portrait_sketch()
