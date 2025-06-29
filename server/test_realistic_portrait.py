import os
import sys
import cv2
import numpy as np
from realistic_portrait_sketch import convert_to_realistic_portrait_sketch

def test_realistic_portrait_sketch():
    """
    Test the realistic portrait sketch functionality with sample images
    """
    try:
        # Debug mode - print current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # Check uploads directory for test images
        upload_dir = os.path.join(current_dir, "uploads")
        print(f"Upload directory: {upload_dir}")
        print(f"Upload directory exists: {os.path.exists(upload_dir)}")
        
        if os.path.exists(upload_dir):
            # List files in uploads directory
            all_files = os.listdir(upload_dir)
            image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(f"Found {len(image_files)} image files in uploads directory")
            
            if image_files:
                # Use the first image file as test
                test_image = os.path.join(upload_dir, image_files[0])
                print(f"Using test image: {test_image}")
                print(f"Test image exists: {os.path.exists(test_image)}")
                
                # Generate sketch without watermark for testing
                sketch_path = convert_to_realistic_portrait_sketch(test_image, add_watermark=False)
                print(f"Generated portrait sketch saved to: {sketch_path}")
                
                # Save a copy to a more accessible location for viewing
                result_dir = os.path.join(current_dir, "portrait_results")
                os.makedirs(result_dir, exist_ok=True)
                
                # Read the sketch and save a copy
                sketch = cv2.imread(sketch_path)
                filename = os.path.basename(test_image)
                result_path = os.path.join(result_dir, f"realistic_portrait_{filename}")
                cv2.imwrite(result_path, sketch)
                
                print(f"Saved copy of result to: {result_path}")
                print("Test completed successfully!")
            else:
                print("No image files found in uploads directory")
        else:
            print("Uploads directory not found")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_realistic_portrait_sketch()

if __name__ == "__main__":
    test_realistic_portrait_sketch()
