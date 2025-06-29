import os
import sys
import cv2
import numpy as np
from improved_sketch import convert_to_authentic_pencil_sketch
from improved_authentic_sketch import convert_to_authentic_pencil_sketch_v2

def test_compare_sketch_versions():
    """
    Test and compare the original and improved authentic pencil sketch algorithms
    """
    # Get the base directory and create test directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    results_dir = os.path.join(base_dir, 'test_results')
    
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
    
    # Use only the first image for this test
    image_file = image_files[0]
    test_image = os.path.join(uploads_dir, image_file)
    print(f"Testing with image: {image_file}")
    
    try:
        # Generate sketches with both methods
        print("\nGenerating original authentic pencil sketch...")
        original_sketch_path = convert_to_authentic_pencil_sketch(test_image, add_watermark=False)
        
        print("\nGenerating improved authentic pencil sketch (V2)...")
        improved_sketch_path = convert_to_authentic_pencil_sketch_v2(test_image, add_watermark=False)
        
        # Save both to the results directory for comparison
        original_result_path = os.path.join(results_dir, "original_authentic_pencil.jpg")
        improved_result_path = os.path.join(results_dir, "improved_authentic_pencil.jpg")
        
        # Move or copy the files to the results directory
        os.replace(original_sketch_path, original_result_path)
        os.replace(improved_sketch_path, improved_result_path)
        
        print("\nResults saved for comparison:")
        print(f"Original: {original_result_path}")
        print(f"Improved: {improved_result_path}")
        
        # Create a side-by-side comparison
        original = cv2.imread(original_result_path)
        improved = cv2.imread(improved_result_path)
        
        # Resize both to the same height if needed
        h1, w1 = original.shape[:2]
        h2, w2 = improved.shape[:2]
        
        if h1 != h2:
            # Resize to match height
            target_height = min(h1, h2)
            scale1 = target_height / h1
            scale2 = target_height / h2
            
            original = cv2.resize(original, (int(w1 * scale1), target_height))
            improved = cv2.resize(improved, (int(w2 * scale2), target_height))
        
        # Create side by side image
        combined = np.hstack((original, improved))
        comparison_path = os.path.join(results_dir, "comparison.jpg")
        cv2.imwrite(comparison_path, combined)
        
        print(f"Side-by-side comparison: {comparison_path}")
        
        # Open the comparison image for viewing
        os.startfile(comparison_path)
        
        # Also open individual images
        os.startfile(original_result_path)
        os.startfile(improved_result_path)
        
    except Exception as e:
        print(f"Error processing comparison: {str(e)}")

if __name__ == "__main__":
    test_compare_sketch_versions()
