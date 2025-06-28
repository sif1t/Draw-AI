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
              "ultra-clear" for ultra-defined lines with maximum clarity,
              "authentic-pencil" for true professional hand-drawn pencil portrait with deep blacks
              (default: artistic)
        
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
            # Ultra-clear sketch for maximum detail and clarity
            
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
            
        elif mode == "authentic-pencil":
            # Authentic professional pencil sketch that truly resembles hand-drawn artwork
            
            # High-resolution processing for fine detail
            height, width = img.shape[:2]
            if max(height, width) > 2000:
                scale_factor = 2000 / max(height, width)
                img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
            elif max(height, width) < 1000:
                # If image is too small, upscale for better detailing
                scale_factor = 1000 / max(height, width)
                img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
                
            height, width = img.shape[:2]
            
            # Superior grayscale conversion using custom color mixing
            if len(img.shape) == 3:
                # Split channels
                b, g, r = cv2.split(img)
                # Custom mixing weights optimized for skin tones and deep blacks
                gray = cv2.addWeighted(r, 0.35, g, 0.4, 0)
                gray = cv2.addWeighted(gray, 0.8, b, 0.2, 0)
            else:
                gray = img.copy()
            
            # Advanced contrast enhancement for deep blacks
            clahe1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray_enhanced = clahe1.apply(gray)
            
            # Apply targeted contrast enhancement 
            lookUpTable = np.empty((1, 256), np.uint8)
            for i in range(256):
                # Deep S-curve for dramatic black pencil effect
                if i < 100:
                    # Make shadows darker
                    lookUpTable[0, i] = np.clip(i * 0.8, 0, 255)
                else:
                    # Keep highlights
                    lookUpTable[0, i] = np.clip(((i - 100) * 0.9) + 80, 0, 255)
            
            gray_contrast = cv2.LUT(gray_enhanced, lookUpTable)
            
            # Multi-layer smoothing with detail preservation
            smooth = cv2.bilateralFilter(gray_contrast, 7, 35, 35)
            
            # Advanced shadow creation for realistic pencil depth
            # Invert the image for shadow creation
            inverted = 255 - smooth
            
            # Multiple blur kernels for realistic pencil shadow gradient
            # Large kernel for deep shadows (like dark hair areas)
            k_deep = int(min(width, height) * 0.04) | 1  # Ensure odd
            blur_deep = cv2.GaussianBlur(inverted, (k_deep, k_deep), 0)
            
            # Medium kernel for transition areas
            k_med = int(min(width, height) * 0.02) | 1  # Ensure odd
            blur_med = cv2.GaussianBlur(inverted, (k_med, k_med), 0)
            
            # Small kernel for fine details and lines
            k_fine = int(min(width, height) * 0.01) | 1  # Ensure odd
            k_fine = max(3, k_fine)  # At least 3
            blur_fine = cv2.GaussianBlur(inverted, (k_fine, k_fine), 0)
            
            # Multi-layered pencil effect with weighted blending
            shadows = cv2.addWeighted(blur_deep, 0.4, blur_med, 0.4, 0)
            shadows = cv2.addWeighted(shadows, 0.8, blur_fine, 0.2, 0)
            
            # Professional dodge effect (creates the pencil-to-paper interaction)
            sketch_base = cv2.divide(smooth, 255 - shadows, scale=256.0)
            
            # Edge refinement for detailed features
            edges = cv2.Laplacian(smooth, cv2.CV_8U, ksize=3)
            _, edges_thresh = cv2.threshold(edges, 15, 255, cv2.THRESH_BINARY_INV)
            edges_soft = cv2.GaussianBlur(edges_thresh, (3, 3), 0.5)
            
            # Layer composition like an artist's technique
            sketch_edge_enhanced = cv2.addWeighted(sketch_base, 0.75, edges_soft, 0.25, 0)
            
            # Create subtle paper texture with grain
            h, w = sketch_edge_enhanced.shape
            np.random.seed(42)  # For consistent results
            fine_grain = np.random.randint(246, 255, (h, w), dtype=np.uint8)
            
            # Create medium scale texture
            h_med, w_med = h//4, w//4
            medium_grain = np.random.randint(240, 255, (h_med, w_med), dtype=np.uint8)
            medium_grain = cv2.resize(medium_grain, (w, h), interpolation=cv2.INTER_LINEAR)
            
            # Blend textures
            paper_texture = np.ones((h, w), dtype=np.uint8) * 252
            paper_grain = cv2.addWeighted(fine_grain, 0.6, medium_grain, 0.4, 0)
            paper_texture = cv2.addWeighted(paper_texture, 0.85, paper_grain, 0.15, 0)
            
            # Apply paper texture to sketch
            result = cv2.multiply(sketch_edge_enhanced, paper_texture, scale=1/255.0)
            
            # Final professional touch - subtle sharpening
            sharpen_kernel = np.array([[-0.2, -0.2, -0.2], 
                                     [-0.2, 3.0, -0.2], 
                                     [-0.2, -0.2, -0.2]])
            result = cv2.filter2D(result, -1, sharpen_kernel)
        
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
    parser.add_argument('-m', '--mode', choices=['regular', 'realistic', 'artistic', 'ultra-clear', 'authentic-pencil'], 
                        default='artistic', help='Sketch mode: "regular" (basic), "realistic" (shaded), "artistic" (portrait), "ultra-clear" (enhanced detail), or "authentic-pencil" (professional hand-drawn) (default: artistic)')
    
    args = parser.parse_args()
    
    # Create the sketch
    result = create_pencil_sketch(args.image_path, args.output, args.mode)
    
    if result is None:
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
