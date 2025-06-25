import os
import cv2
import argparse
import sys
from improved_sketch import convert_to_pencil_sketch, convert_to_realistic_pencil_sketch

def test_improved_sketch(image_path, output_dir=None):
    """
    Test the improved sketch algorithms on an image.
    
    Args:
        image_path: Path to the input image
        output_dir: Directory to save output images (default: same as input)
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return False
    
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get file name without extension
    base_name = os.path.basename(image_path).split('.')[0]
    
    try:
        # Test regular pencil sketch
        print("Testing regular pencil sketch...")
        pencil_path = convert_to_pencil_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        pencil_output = os.path.join(output_dir, f"{base_name}_pencil_sketch.jpg")
        img = cv2.imread(pencil_path)
        cv2.imwrite(pencil_output, img)
        print(f"Regular pencil sketch saved to: {pencil_output}")
        
        # Test realistic pencil sketch
        print("Testing realistic pencil sketch...")
        realistic_path = convert_to_realistic_pencil_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        realistic_output = os.path.join(output_dir, f"{base_name}_realistic_sketch.jpg")
        img = cv2.imread(realistic_path)
        cv2.imwrite(realistic_output, img)
        print(f"Realistic pencil sketch saved to: {realistic_output}")
        
        return True
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test improved sketch algorithms')
    parser.add_argument('image', help='Path to input image')
    parser.add_argument('-o', '--output', help='Output directory')
    
    args = parser.parse_args()
    
    success = test_improved_sketch(args.image, args.output)
    
    if success:
        print("Testing completed successfully")
        return 0
    else:
        print("Testing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
