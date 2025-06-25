import os
import cv2
import numpy as np
from PIL import Image
import argparse
import sys
import sys

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server'))

# Now import the sketch modules
import sketch
import improved_sketch

def compare_sketch_methods(image_path, output_dir=None):
    """
    Compare different sketch methods on the same image
    
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
        # Create comparison image
        results = []
        labels = []
        
        # Original image
        original = cv2.imread(image_path)
        h, w = original.shape[:2]
        results.append(original)
        labels.append("Original")
        
        # Original method
        print("Testing original sketch method...")
        try:
            original_sketch_path = sketch.convert_to_sketch(image_path, add_watermark=False)
            original_sketch = cv2.imread(original_sketch_path)
            results.append(original_sketch)
            labels.append("Original Method")
        except Exception as e:
            print(f"Error with original method: {str(e)}")
        
        # New pencil sketch
        print("Testing new pencil sketch method...")
        try:
            pencil_path = improved_sketch.convert_to_pencil_sketch(image_path, add_watermark=False)
            pencil_sketch = cv2.imread(pencil_path)
            results.append(pencil_sketch)
            labels.append("New Pencil Sketch")
        except Exception as e:
            print(f"Error with pencil sketch: {str(e)}")
        
        # New realistic sketch
        print("Testing new realistic sketch method...")
        try:
            realistic_path = improved_sketch.convert_to_realistic_pencil_sketch(image_path, add_watermark=False)
            realistic_sketch = cv2.imread(realistic_path)
            results.append(realistic_sketch)
            labels.append("New Realistic Sketch")
        except Exception as e:
            print(f"Error with realistic sketch: {str(e)}")
        
        # Create comparison grid
        rows = len(results)
        grid_h = rows * h
        grid_w = w
        grid = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)
        
        # Add each result to the grid
        for i, img in enumerate(results):
            if img is not None:
                grid[i*h:(i+1)*h, 0:w] = img
        
        # Add text labels
        for i, label in enumerate(labels):
            y = i * h + 30
            cv2.putText(grid, label, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Save comparison grid
        comparison_path = os.path.join(output_dir, f"{base_name}_comparison.jpg")
        cv2.imwrite(comparison_path, grid)
        print(f"Comparison saved to: {comparison_path}")
        
        return True
    except Exception as e:
        print(f"Error during comparison: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Compare different sketch methods')
    parser.add_argument('image', help='Path to input image')
    parser.add_argument('-o', '--output', help='Output directory')
    
    args = parser.parse_args()
    
    success = compare_sketch_methods(args.image, args.output)
    
    if success:
        print("Comparison completed successfully")
        return 0
    else:
        print("Comparison failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
