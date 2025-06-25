import os
import cv2
import argparse
import sys
import improved_sketch

def test_all_sketch_styles(image_path, output_dir=None):
    """
    Test all available sketch styles on an image.
    
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
        print("\n1. Testing basic pencil sketch...")
        pencil_path = improved_sketch.convert_to_pencil_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        pencil_output = os.path.join(output_dir, f"{base_name}_pencil_sketch.jpg")
        img = cv2.imread(pencil_path)
        cv2.imwrite(pencil_output, img)
        print(f"Basic pencil sketch saved to: {pencil_output}")
        
        # Test realistic pencil sketch
        print("\n2. Testing realistic pencil sketch...")
        realistic_path = improved_sketch.convert_to_realistic_pencil_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        realistic_output = os.path.join(output_dir, f"{base_name}_realistic_sketch.jpg")
        img = cv2.imread(realistic_path)
        cv2.imwrite(realistic_output, img)
        print(f"Realistic pencil sketch saved to: {realistic_output}")
        
        # Test artistic portrait sketch
        print("\n3. Testing artistic portrait sketch...")
        portrait_path = improved_sketch.convert_to_artistic_portrait_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        portrait_output = os.path.join(output_dir, f"{base_name}_artistic_portrait.jpg")
        img = cv2.imread(portrait_path)
        cv2.imwrite(portrait_output, img)
        print(f"Artistic portrait sketch saved to: {portrait_output}")
        
        # Test ultra-clear sketch
        print("\n4. Testing ultra-clear sketch...")
        ultra_path = improved_sketch.convert_to_ultra_clear_sketch(image_path, add_watermark=False)
        
        # Copy to output dir with more descriptive name
        ultra_output = os.path.join(output_dir, f"{base_name}_ultra_clear.jpg")
        img = cv2.imread(ultra_path)
        cv2.imwrite(ultra_output, img)
        print(f"Ultra-clear sketch saved to: {ultra_output}")
        
        print("\nAll sketch styles generated successfully!")
        return True
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test all available sketch styles')
    parser.add_argument('image', help='Path to input image')
    parser.add_argument('-o', '--output', help='Output directory')
    
    args = parser.parse_args()
    
    success = test_all_sketch_styles(args.image, args.output)
    
    if success:
        print("\nTesting completed successfully. Please check the output files to see which style best matches your requirements.")
        return 0
    else:
        print("\nTesting failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
