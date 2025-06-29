import os
import sys
import cv2
import numpy as np
from enhanced_realistic_portrait_sketch import convert_to_realistic_portrait_sketch

def test_enhanced_realistic_portrait_sketch():
    """
    Test the enhanced realistic portrait sketch functionality with sample images
    """
    try:
        # Debug mode - print current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # First check if there are any portrait test images in the uploads directory
        upload_dir = os.path.join(current_dir, "uploads")
        print(f"Upload directory: {upload_dir}")
        print(f"Upload directory exists: {os.path.exists(upload_dir)}")
        
        # Test files - look in any available directory for valid images
        test_locations = [
            os.path.join(current_dir, "uploads"),
            os.path.join(current_dir, "..")  # Parent directory
        ]
        
        found_images = False
        
        for loc in test_locations:
            if os.path.exists(loc):
                print(f"Checking directory: {loc}")
                all_files = os.listdir(loc)
                image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                print(f"Found {len(image_files)} image files in {loc}")
                
                if image_files:
                    found_images = True
                    upload_dir = loc
                    break
        
        if found_images:
                # Look for portrait/face images first
                portrait_keywords = ['face', 'portrait', 'person', 'profile', 'selfie']
                portrait_images = [f for f in image_files if any(keyword in f.lower() for keyword in portrait_keywords)]
                
                # If no portrait images found, use any image
                test_images = portrait_images if portrait_images else image_files
                
                # Use the first image file as test
                test_image = os.path.join(upload_dir, test_images[0])
                print(f"Using test image: {test_image}")
                print(f"Test image exists: {os.path.exists(test_image)}")
                
                # Generate sketch without watermark for testing
                sketch_path = convert_to_realistic_portrait_sketch(test_image, add_watermark=False)
                print(f"Generated enhanced portrait sketch saved to: {sketch_path}")
                
                # Save a copy to a more accessible location for viewing
                result_dir = os.path.join(current_dir, "portrait_results")
                os.makedirs(result_dir, exist_ok=True)
                
                # Read the sketch and save a copy
                sketch = cv2.imread(sketch_path)
                if sketch is not None:
                    filename = os.path.basename(test_image)
                    result_path = os.path.join(result_dir, f"enhanced_portrait_{filename}")
                    cv2.imwrite(result_path, sketch)
                    
                    print(f"Saved copy of result to: {result_path}")
                    print("Test completed successfully!")
                else:
                    print(f"Failed to read the generated sketch from {sketch_path}")
        else:
            # If no images found in any directory, create a sample test image
            print("No suitable test images found. Creating a test gradient image...")
            
            # Create a basic gradient test image
            test_img = np.zeros((800, 600), dtype=np.uint8)
            for i in range(800):
                test_img[i, :] = i // 3
                
            # Add some features to simulate a face
            cv2.circle(test_img, (300, 300), 200, 200, -1)  # Head
            cv2.circle(test_img, (240, 250), 30, 100, -1)   # Left eye
            cv2.circle(test_img, (360, 250), 30, 100, -1)   # Right eye
            cv2.ellipse(test_img, (300, 350), (80, 40), 0, 0, 180, 150, -1)  # Mouth
            
            # Save the test image
            test_dir = os.path.join(current_dir, "test_images")
            os.makedirs(test_dir, exist_ok=True)
            test_image = os.path.join(test_dir, "test_face.jpg")
            cv2.imwrite(test_image, test_img)
            print(f"Created test image at: {test_image}")
            
            # Generate sketch without watermark for testing
            sketch_path = convert_to_realistic_portrait_sketch(test_image, add_watermark=False)
            print(f"Generated enhanced portrait sketch saved to: {sketch_path}")
            
            # Save a copy to a more accessible location for viewing
            result_dir = os.path.join(current_dir, "portrait_results")
            os.makedirs(result_dir, exist_ok=True)
            
            # Read the sketch and save a copy
            sketch = cv2.imread(sketch_path)
            if sketch is not None:
                result_path = os.path.join(result_dir, "enhanced_portrait_test_face.jpg")
                cv2.imwrite(result_path, sketch)
                
                print(f"Saved copy of result to: {result_path}")
                print("Test completed successfully!")
            else:
                print(f"Failed to read the generated sketch from {sketch_path}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_realistic_portrait_sketch()
