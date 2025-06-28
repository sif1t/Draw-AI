import os
import sys
import cv2
from improved_sketch import convert_to_authentic_pencil_sketch

def test_authentic_pencil_sketch():
    """
    Test the authentic pencil sketch generation function
    """
    # Get the base directory and create test directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    
    # Ensure the uploads directory exists
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Check if there are images in the uploads directory
    image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("No test images found in the uploads directory.")
        print("Please place at least one image in the uploads directory.")
        return
    
    # Process the first image found
    test_image = os.path.join(uploads_dir, image_files[0])
    print(f"Testing authentic pencil sketch conversion with image: {test_image}")
    
    try:
        # Generate a sketch with watermark
        watermarked_sketch = convert_to_authentic_pencil_sketch(test_image, add_watermark=True)
        print(f"Generated watermarked sketch: {watermarked_sketch}")
        
        # Generate a sketch without watermark
        no_watermark_sketch = convert_to_authentic_pencil_sketch(test_image, add_watermark=False)
        print(f"Generated sketch without watermark: {no_watermark_sketch}")
        
        # Verify files were created
        if os.path.exists(watermarked_sketch) and os.path.exists(no_watermark_sketch):
            print("✅ Both sketches successfully generated!")
            
            # Open the images for viewing (Windows)
            os.startfile(watermarked_sketch)
            os.startfile(no_watermark_sketch)
        else:
            print("❌ Error: One or both sketch files were not created.")
            
    except Exception as e:
        print(f"❌ Error during authentic pencil sketch conversion: {str(e)}")

if __name__ == "__main__":
    test_authentic_pencil_sketch()
