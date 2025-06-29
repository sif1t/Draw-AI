import os
import sys
import cv2
import numpy as np
import glob
from realistic_portrait_sketch import convert_to_realistic_portrait_sketch

def test_batch_enhanced_portrait():
    """
    Test the enhanced realistic portrait sketch functionality with multiple portrait images
    """
    try:
        # Debug mode - print current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # Check uploads directory for test images
        upload_dir = os.path.join(current_dir, "uploads")
        print(f"Upload directory: {upload_dir}")
        
        if not os.path.exists(upload_dir):
            print("Uploads directory not found")
            return
            
        # Create results directory
        result_dir = os.path.join(current_dir, "portrait_results")
        os.makedirs(result_dir, exist_ok=True)
        
        # Look for portrait/face images
        portrait_keywords = ['face', 'portrait', 'person', 'profile', 'selfie']
        
        # Use glob to find all image files in the uploads directory
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(glob.glob(os.path.join(upload_dir, ext)))
            
        # Filter for portrait images
        portrait_images = [f for f in image_files if any(keyword in os.path.basename(f).lower() for keyword in portrait_keywords)]
        
        # If no portrait images found, use first few images
        test_images = portrait_images if portrait_images else image_files[:3]
        
        # Limit to first 5 images for batch testing
        test_images = test_images[:5]
        
        print(f"Found {len(test_images)} test images")
        
        # Process each test image
        for i, test_image in enumerate(test_images):
            print(f"\nProcessing test image {i+1}/{len(test_images)}: {os.path.basename(test_image)}")
            
            try:
                # Generate sketch without watermark for testing
                sketch_path = convert_to_realistic_portrait_sketch(test_image, add_watermark=False)
                print(f"Generated sketch saved to: {sketch_path}")
                
                # Read the sketch and save a copy with a descriptive name
                sketch = cv2.imread(sketch_path)
                if sketch is not None:
                    filename = os.path.basename(test_image)
                    result_path = os.path.join(result_dir, f"enhanced_portrait_{i+1}_{filename}")
                    cv2.imwrite(result_path, sketch)
                    
                    print(f"Saved copy of result to: {result_path}")
                else:
                    print(f"Failed to read the generated sketch from {sketch_path}")
            except Exception as e:
                print(f"Error processing image {test_image}: {str(e)}")
                
        print("\nBatch test completed!")
        
    except Exception as e:
        print(f"Error during batch test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_batch_enhanced_portrait()
