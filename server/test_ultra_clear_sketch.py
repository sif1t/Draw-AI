import os
import sys
import cv2
from improved_sketch import convert_to_ultra_clear_sketch

def test_ultra_clear_sketch():
    """
    Test the ultra-clear sketch conversion
    """
    # Get directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if a file was provided as command line argument
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if not os.path.exists(input_path):
            print(f"Error: File {input_path} not found")
            return
    else:
        # Look for any image in the uploads folder for testing
        uploads_dir = os.path.join(script_dir, "uploads")
        if not os.path.exists(uploads_dir):
            print(f"Error: Uploads directory {uploads_dir} not found")
            return
            
        # Find the first image file in the uploads directory
        image_found = False
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(uploads_dir, filename)
                image_found = True
                break
                
        if not image_found:
            print("Error: No image files found in uploads directory")
            return
    
    print(f"Testing ultra-clear sketch conversion with image: {input_path}")
    
    try:
        # Convert image to ultra-clear sketch
        output_path = convert_to_ultra_clear_sketch(input_path, add_watermark=True)
        
        print(f"Ultra-clear sketch generated successfully: {output_path}")
        
        # Verify the output file exists
        if os.path.exists(output_path):
            print("Test PASSED: Output file created successfully")
            
            # Get file size and dimensions
            output_size = os.path.getsize(output_path) / 1024  # KB
            img = cv2.imread(output_path)
            height, width = img.shape[:2]
            
            print(f"Output image dimensions: {width}x{height}")
            print(f"Output file size: {output_size:.2f} KB")
            
            # Optional: Open the image to visually verify (if in an environment with GUI)
            # import matplotlib.pyplot as plt
            # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            # plt.title("Ultra-Clear Sketch")
            # plt.axis('off')
            # plt.show()
            
        else:
            print("Test FAILED: Output file not found")
    
    except Exception as e:
        print(f"Test FAILED: Error during conversion - {str(e)}")

if __name__ == "__main__":
    test_ultra_clear_sketch()
