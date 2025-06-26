import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import sys

def create_pencil_sketch(image_path, output_path=None, mode="artistic"):
    """
    Create a pencil sketch from an image.
    
    Args:
        image_path: Path to the input image
        output_path: Path to save the output image (if None, will use input name + _sketch)
        mode: "regular" for standard sketch, 
              "realistic" for realistic sketch with shading, 
              "artistic" for professional artist-quality portrait sketch,
              "ultra-clear" for ultra-defined lines with maximum clarity (default: artistic)
        
    Returns:
        Path to the generated sketch image
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return None
            
        # Generate default output path if not provided
        if output_path is None:
            base_name = os.path.splitext(image_path)[0]
            output_path = f"{base_name}_sketch.jpg"
        
        if mode == "regular":
            # Regular sketch method
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect edges
            edges = cv2.Laplacian(gray_blur, cv2.CV_8U, ksize=5)
            
            # Threshold to create binary image
            _, sketch = cv2.threshold(edges, 30, 255, cv2.THRESH_BINARY_INV)
            
            # Final sketch
            result = sketch
            
        elif mode == "realistic":
            # Realistic sketch with shading
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Invert the grayscale image
            inverted = 255 - gray
            
            # Apply Gaussian blur to the inverted image
            blur = cv2.GaussianBlur(inverted, (21, 21), 0)
            
            # Invert the blurred image
            inverted_blur = 255 - blur
            
            # Blend the grayscale image with the inverted blurred image
            result = cv2.divide(gray, inverted_blur, scale=256.0)
            
            # Enhance contrast for better definition
            result = cv2.convertScaleAbs(result, alpha=1.2, beta=10)
            
        elif mode == "artistic":
            # Artistic portrait sketch (professional quality)
            
            # Enhanced pre-processing for portrait-quality 
            # Convert to grayscale with enhanced portrait weights
            if len(img.shape) == 3:
                b, g, r = cv2.split(img)
                gray = cv2.addWeighted(cv2.addWeighted(r, 0.33, g, 0.33, 0), 0.7, b, 0.3, 0)
            else:
                gray = img.copy()
                
            # Enhance all details with adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Multi-level detail preservation
            smooth1 = cv2.bilateralFilter(gray, 5, 75, 75)
            smooth2 = cv2.bilateralFilter(gray, 9, 150, 150)
            smooth = cv2.addWeighted(smooth1, 0.6, smooth2, 0.4, 0)
            
            # Inverted for shading
            inverted = 255 - smooth
            
            # Create broad shading with adaptive kernel size
            h, w = gray.shape[:2]
            kernel_size = max(int(min(w, h) * 0.04) | 1, 11)
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            # Make sure second kernel size is odd
            kernel_size2 = max(kernel_size//2, 3)
            if kernel_size2 % 2 == 0:
                kernel_size2 += 1
                
            # Create realistic shading
            blur1 = cv2.GaussianBlur(inverted, (kernel_size, kernel_size), 0)
            blur2 = cv2.GaussianBlur(inverted, (kernel_size2, kernel_size2), 0)
            combined_shade = cv2.addWeighted(blur1, 0.7, blur2, 0.3, 0)
            
            # Create base sketch with dodge blend
            sketch_base = cv2.divide(smooth, 255 - combined_shade, scale=256.0)
            
            # Add edge details for artistic effect
            edges = cv2.Laplacian(smooth, cv2.CV_8U, ksize=5)
            _, edges_thresh = cv2.threshold(edges, 20, 255, cv2.THRESH_BINARY_INV)
            edges_blur = cv2.GaussianBlur(edges_thresh, (3, 3), 0)
            
            # Blend for artistic effect
            result = cv2.addWeighted(sketch_base, 0.8, edges_blur, 0.2, 0)
            
            # Final contrast enhancement
            result = cv2.convertScaleAbs(result, alpha=1.2, beta=5)
            
        elif mode == "ultra-clear":
            # Authentic pencil sketch that mimics real hand-drawn artwork
            
            # Convert to grayscale with natural pencil-friendly weights
            if len(img.shape) == 3:
                b, g, r = cv2.split(img)
                gray = cv2.addWeighted(cv2.addWeighted(r, 0.35, g, 0.45, 0), 0.8, b, 0.2, 0)
            else:
                gray = img.copy()
            
            # Apply advanced detail enhancement
            clahe1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            clahe2 = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
            gray_enhanced = clahe1.apply(gray)
            gray_enhanced = clahe2.apply(gray_enhanced)
            
            # Edge-preserving noise reduction
            denoise = cv2.bilateralFilter(gray_enhanced, 5, 15, 15)
            
            # Ultra-precise edge detection (multi-scale approach)
            edges1 = cv2.Laplacian(denoise, cv2.CV_8U, ksize=1)
            edges2 = cv2.Laplacian(denoise, cv2.CV_8U, ksize=3)
            edges3 = cv2.Laplacian(denoise, cv2.CV_8U, ksize=5)
            
            # Normalize and combine edge maps
            _, edges1_thresh = cv2.threshold(edges1, 5, 255, cv2.THRESH_BINARY_INV)
            _, edges2_thresh = cv2.threshold(edges2, 10, 255, cv2.THRESH_BINARY_INV)
            _, edges3_thresh = cv2.threshold(edges3, 15, 255, cv2.THRESH_BINARY_INV)
            
            # Combine edges with weighted importance
            edge_map = cv2.addWeighted(
                cv2.addWeighted(edges1_thresh, 0.5, edges2_thresh, 0.3, 0),
                0.8, edges3_thresh, 0.2, 0
            )
            
            # High-definition shading base
            inverted = 255 - denoise
            
            # Multi-scale blurring for natural gradient transitions
            blur1 = cv2.GaussianBlur(inverted, (15, 15), 0)  # Broad shading
            blur2 = cv2.GaussianBlur(inverted, (7, 7), 0)    # Medium details
            blur3 = cv2.GaussianBlur(inverted, (3, 3), 0)    # Fine details
            
            # Combine blurs with precise weighting
            combined_blur = cv2.addWeighted(
                cv2.addWeighted(blur1, 0.4, blur2, 0.4, 0),
                0.7, blur3, 0.3, 0
            )
            
            # Apply dodge blend for base sketch
            sketch_base = cv2.divide(denoise, 255 - combined_blur, scale=256.0)
            
            # Apply unsharp mask for extreme clarity
            gaussian = cv2.GaussianBlur(sketch_base, (0, 0), 3.0)
            unsharp = cv2.addWeighted(sketch_base, 2.0, gaussian, -1.0, 0)
            
            # Merge with edge details for ultra-crisp lines
            sketch_with_edges = cv2.addWeighted(unsharp, 0.6, edge_map, 0.4, 0)
            
            # Apply extreme contrast enhancement
            sketch_contrast = cv2.convertScaleAbs(sketch_with_edges, alpha=1.5, beta=-15)
            
            # Apply additional local contrast enhancement
            clahe_final = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(3, 3))
            sketch_contrast = clahe_final.apply(sketch_contrast)
            
            # Apply sharpening for final definition
            sharpen_kernel = np.array([[-0.4, -0.4, -0.4], 
                                     [-0.4,  5.2, -0.4], 
                                     [-0.4, -0.4, -0.4]])
            result = cv2.filter2D(sketch_contrast, -1, sharpen_kernel)
            
        else:
            print(f"Error: Invalid mode '{mode}'. Use 'regular', 'realistic', 'artistic', or 'ultra-clear'.")
            return None
        
        # Save the sketch
        cv2.imwrite(output_path, result)
        print(f"Sketch saved to {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"Error creating pencil sketch: {str(e)}")
        return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert an image to a pencil sketch.')
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('-o', '--output', help='Path to save the output image')
    parser.add_argument('-m', '--mode', choices=['regular', 'realistic', 'artistic', 'ultra-clear'], 
                        default='artistic', help='Sketch mode: "regular" (basic), "realistic" (shaded), "artistic" (portrait), or "ultra-clear" (authentic hand-drawn) (default: artistic)')
    
    args = parser.parse_args()
    
    # Create the sketch
    result = create_pencil_sketch(args.image_path, args.output, args.mode)
    
    if result is None:
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
