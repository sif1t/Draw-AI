import os
import sys
import cv2
import numpy as np
from improved_sketch import convert_to_authentic_pencil_sketch

def test_professional_pencil_sketch():
    """
    Test the enhanced professional-looking authentic pencil sketch
    with darker blacks and more contrast
    """
    # Get the base directory and create test directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    results_dir = os.path.join(base_dir, 'professional_pencil_results')
    
    # Ensure directories exist
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Get all images in the uploads directory
    image_files = [f for f in os.listdir(uploads_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("No test images found in the uploads directory.")
        print("Please place at least one image in the uploads directory.")
        return
    
    # Use the first three images or less if fewer are available
    test_images = image_files[:min(3, len(image_files))]
    print(f"Testing professional-looking pencil sketch with {len(test_images)} images...")
    
    for idx, image_file in enumerate(test_images):
        print(f"\nProcessing image {idx + 1}/{len(test_images)}: {image_file}")
        test_image = os.path.join(uploads_dir, image_file)
        
        # Generate sketch
        sketch_path = convert_to_authentic_pencil_sketch(test_image, add_watermark=False)
        print(f"Professional pencil sketch generated: {sketch_path}")
        
        # Move to results directory with descriptive name
        base_name = os.path.splitext(image_file)[0]
        result_path = os.path.join(results_dir, f"{base_name}_professional_pencil.jpg")
        
        # Copy to results directory
        img = cv2.imread(sketch_path)
        cv2.imwrite(result_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"Saved to: {result_path}")
        
        # Open for viewing
        os.startfile(result_path)
    
    print("\n✅ Professional pencil sketch testing completed!")
    print(f"Results saved in: {results_dir}")

if __name__ == "__main__":
    test_professional_pencil_sketch()
