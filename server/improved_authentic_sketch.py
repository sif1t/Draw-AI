import os
import sys
import uuid
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

def convert_to_authentic_pencil_sketch_v2(image_path, add_watermark=True):
    """
    Convert an image to an authentic hand-drawn pencil sketch with NO circular
    or square artifacts. This version specifically addresses texture issues by
    using asymmetric kernels, non-uniform noise, and advanced blending techniques.
    
    Args:
        image_path: Path to the input image
        add_watermark: Boolean to determine if watermark should be added
    
    Returns:
        Path to the generated sketch image
    """
    print(f"Converting image to artifact-free authentic pencil sketch. Add watermark: {add_watermark}")
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Read the image with error handling
        img = cv2.imread(image_path)
        
        # Check if image was successfully loaded
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Step 1: Process at high resolution
        max_dimension = 2500  # High but not excessive resolution
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale_factor = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
        elif max(height, width) < 1200:  # If image is too small, upscale
            scale_factor = 1200 / max(height, width)
            img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        height, width = img.shape[:2]
        
        # Step 2: Improved grayscale conversion using perceptual weights
        if len(img.shape) == 3:
            # Convert using perceptual luminance-preserving weights
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply additional weighting for portraits to enhance skin tones
            b, g, r = cv2.split(img)
            gray_custom = cv2.addWeighted(r, 0.33, g, 0.45, 0)
            gray_custom = cv2.addWeighted(gray_custom, 0.85, b, 0.15, 0)
            
            # Blend standard and custom grayscale
            gray = cv2.addWeighted(gray, 0.5, gray_custom, 0.5, 0)
        else:
            gray = img.copy()
            
        # Step 3: Apply local contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray_enhanced = clahe.apply(gray)
        
        # Apply bilateral filter to preserve edges but smooth noise
        smooth = cv2.bilateralFilter(gray_enhanced, 9, 25, 25)
        
        # Step 4: Enhance portrait-specific areas if present
        # Calculate a face-priority region
        face_region = smooth[int(height*0.15):int(height*0.85), 
                          int(width*0.15):int(width*0.85)].copy()
        
        # Enhance details in face region
        clahe_face = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(4, 4))
        face_enhanced = clahe_face.apply(face_region)
        
        # Apply back to the image
        smooth_with_face = smooth.copy()
        smooth_with_face[int(height*0.15):int(height*0.85), 
                       int(width*0.15):int(width*0.85)] = face_enhanced
        
        # Step 5: Create shadows using multiple techniques to avoid patterns
        inverted = 255 - smooth_with_face
        
        # Use asymmetric box blur + Gaussian blur combinations 
        # with prime-number dimensions to avoid grid patterns
        
        # Deep shadows (use box blur to avoid circular patterns)
        k_box_1 = (23, 17)  # Prime number sizes
        k_box_2 = (19, 29)  # Different prime numbers
        blur_box_1 = cv2.boxFilter(inverted, -1, k_box_1)
        blur_box_2 = cv2.boxFilter(inverted, -1, k_box_2)
        
        # Mix them with different weights
        deep_shadows = cv2.addWeighted(blur_box_1, 0.6, blur_box_2, 0.4, 0)
        
        # Medium shadows (use median blur for some areas - no circular pattern)
        blur_med1 = cv2.GaussianBlur(inverted, (13, 13), 0)
        blur_med2 = cv2.medianBlur(inverted, 13)  # Median blur has no directional bias
        medium_shadows = cv2.addWeighted(blur_med1, 0.7, blur_med2, 0.3, 0)
        
        # Fine details (smaller kernels)
        blur_fine = cv2.GaussianBlur(inverted, (7, 7), 0)
        
        # Combine shadow layers with varied blending to avoid repeating patterns
        shadows_temp = cv2.addWeighted(deep_shadows, 0.45, medium_shadows, 0.55, 0)
        
        # Apply directional blur to break up any remaining patterns
        # This spreads any potential artifacts in a way that looks more like pencil strokes
        motion_blur_kernel_size = 9
        # Create motion blur kernel at an angle
        motion_kernel = np.zeros((motion_blur_kernel_size, motion_blur_kernel_size))
        motion_kernel[motion_blur_kernel_size//2, :] = 1.0 / motion_blur_kernel_size
        motion_shadows = cv2.filter2D(shadows_temp, -1, motion_kernel)
        
        # Rotate and apply again at different angle
        motion_kernel_2 = np.zeros((motion_blur_kernel_size, motion_blur_kernel_size))
        motion_kernel_2[:, motion_blur_kernel_size//2] = 1.0 / motion_blur_kernel_size
        motion_shadows_2 = cv2.filter2D(shadows_temp, -1, motion_kernel_2)
        
        # Add motion-blurred versions to further break up patterns
        shadows_with_motion = cv2.addWeighted(shadows_temp, 0.7, 
                                              cv2.addWeighted(motion_shadows, 0.5, motion_shadows_2, 0.5, 0), 
                                              0.3, 0)
        
        # Add fine details on top
        shadows_final = cv2.addWeighted(shadows_with_motion, 0.85, blur_fine, 0.15, 0)
        
        # Step 6: Apply dodge effect for the pencil look
        # Use a safer division method with added offset to avoid artifacts in bright areas
        dodge_divisor = 255 - shadows_final
        dodge_divisor = np.maximum(dodge_divisor, 5)  # Avoid division by very small numbers
        dodge = (smooth_with_face.astype(np.float32) * 255.0) / dodge_divisor.astype(np.float32)
        dodge = np.clip(dodge, 0, 255).astype(np.uint8)
        
        # Step 7: Edge enhancement using multiple edge detectors
        # Use multiple edge detection methods and blend them
        
        # Sobel edges with different orientations
        sobel_h = cv2.Sobel(smooth_with_face, cv2.CV_8U, 1, 0, ksize=3)
        sobel_v = cv2.Sobel(smooth_with_face, cv2.CV_8U, 0, 1, ksize=3)
        # For diagonal, use both x and y derivatives but avoid negative values
        sobel_diag1 = cv2.Sobel(smooth_with_face, cv2.CV_8U, 1, 1, ksize=3)
        # For second diagonal, use separate calculations and combine
        sobel_x2 = cv2.Sobel(smooth_with_face, cv2.CV_8U, 1, 0, ksize=3)
        sobel_y2 = cv2.Sobel(smooth_with_face, cv2.CV_8U, 0, 1, ksize=3)
        sobel_diag2 = cv2.absdiff(sobel_x2, sobel_y2)
        
        # Combine with different weights to avoid grid patterns
        sobel_combined = (sobel_h * 0.25 + sobel_v * 0.25 + 
                         sobel_diag1 * 0.25 + sobel_diag2 * 0.25).astype(np.uint8)
        
        # Laplacian edge detection
        laplacian = cv2.Laplacian(smooth_with_face, cv2.CV_8U)
        
        # Canny edge detector for fine lines
        canny = cv2.Canny(smooth_with_face, 30, 90)
        
        # Combine edges with different weights
        edges_combined = cv2.addWeighted(sobel_combined, 0.4, laplacian, 0.3, 0)
        edges_combined = cv2.addWeighted(edges_combined, 0.7, canny, 0.3, 0)
        
        # Use adaptive thresholding to enhance edges naturally
        edges_thresh = cv2.adaptiveThreshold(
            edges_combined, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2)
        
        # Smooth edges
        edges_smooth = cv2.GaussianBlur(edges_thresh, (3, 3), 0.8)
        
        # Step 8: Combine base sketch with edges naturally
        # Only apply edges where they matter (near actual content transitions)
        gradient_mag = cv2.convertScaleAbs(
            cv2.Sobel(dodge, cv2.CV_32F, 1, 1, ksize=3))
        _, gradient_mask = cv2.threshold(gradient_mag, 10, 255, cv2.THRESH_BINARY)
        
        # Apply edge enhancements only where needed
        edges_masked = cv2.bitwise_and(edges_smooth, edges_smooth, mask=gradient_mask)
        sketch_enhanced = cv2.addWeighted(dodge, 0.85, edges_masked, 0.15, 0)
        
        # Step 9: Apply tone adjustment for rich darks
        # Custom tone curve for authentic pencil look
        tone_curve = np.empty((1, 256), np.uint8)
        for i in range(256):
            if i < 50:  # Very dark areas - make them darker
                tone_curve[0, i] = np.clip(i * 0.6, 0, 255)
            elif i < 150:  # Mid tones
                tone_curve[0, i] = np.clip(((i - 50) * 0.9) + 30, 0, 255)
            else:  # Highlights - preserve paper white
                tone_curve[0, i] = np.clip(((i - 150) * 1.2) + 120, 0, 255)
        
        sketch_toned = cv2.LUT(sketch_enhanced, tone_curve)
        
        # Step 10: Create non-repetitive paper texture
        # Use a mix of different noise patterns at multiple scales
        
        # Start with slightly off-white base
        h, w = sketch_toned.shape
        paper = np.ones((h, w), dtype=np.uint8) * 252
        
        # Use multiple random seeds to avoid correlation
        np.random.seed(42)
        fine_noise = np.random.randint(245, 255, (h, w), dtype=np.uint8)
        
        np.random.seed(13)  # Different seed
        # Use prime number divisions to avoid regular patterns
        med_noise1 = cv2.resize(
            np.random.randint(240, 255, (h//11, w//13), dtype=np.uint8), 
            (w, h), interpolation=cv2.INTER_LINEAR)
            
        np.random.seed(97)  # Another prime
        med_noise2 = cv2.resize(
            np.random.randint(235, 255, (h//17, w//19), dtype=np.uint8), 
            (w, h), interpolation=cv2.INTER_LINEAR)
            
        # Combine noise patterns
        paper_texture = cv2.addWeighted(fine_noise, 0.3, med_noise1, 0.4, 0)
        paper_texture = cv2.addWeighted(paper_texture, 0.8, med_noise2, 0.2, 0)
        
        # Add very subtle non-uniform blur to remove any pixel patterns
        # This creates a more natural paper grain
        kernel_sizes = [3, 5]
        blur_weights = [0.7, 0.3]
        blurred_textures = []
        
        for i, k_size in enumerate(kernel_sizes):
            # Apply slight blur
            blurred = cv2.GaussianBlur(paper_texture, (k_size, k_size), 0)
            # Weight it
            blurred_textures.append(blurred * blur_weights[i])
            
        # Recombine
        paper_texture = sum(blurred_textures).astype(np.uint8)
        
        # Combine with base paper
        paper_texture = cv2.addWeighted(paper, 0.85, paper_texture, 0.15, 0)
        
        # Step 11: Apply paper texture to sketch
        # Use multiply blend mode
        sketch_on_paper = (sketch_toned.astype(np.float32) * paper_texture.astype(np.float32) / 255.0).astype(np.uint8)
        
        # Step 12: Add natural pencil stroke variation
        # Use non-uniform 2D Perlin-like noise instead of regular patterns
        
        # Create multiple noise layers with prime number sizes and offsets
        np.random.seed(42)  # Reset seed
        noise_layers = []
        
        # Prime number sizes to avoid regular patterns
        noise_dims = [(h//7, w//11), (h//13, w//17), (h//19, w//23)]
        for i, dims in enumerate(noise_dims):
            np.random.seed(37 + i*17)  # Different seeds
            noise = np.random.randint(0, 10-i*2, dims, dtype=np.uint8)  # Decreasing intensity
            noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_LINEAR)
            noise_layers.append(noise * (0.5 / (i+1)))  # Decreasing weights
            
        # Combine noise layers
        combined_noise = sum(noise_layers).astype(np.uint8)
        
        # Apply slight blur to make noise pattern more natural
        combined_noise = cv2.GaussianBlur(combined_noise, (3, 3), 0.5)
        
        # Create masks for different tone areas - with overlap
        # Apply noise differently to different tonal regions
        _, shadow_mask = cv2.threshold(sketch_toned, 60, 255, cv2.THRESH_BINARY_INV)
        _, midtone_mask = cv2.threshold(sketch_toned, 180, 255, cv2.THRESH_BINARY_INV)
        midtone_mask = cv2.subtract(midtone_mask, shadow_mask)
        
        # Smooth masks
        shadow_mask = cv2.GaussianBlur(shadow_mask, (7, 7), 0)
        midtone_mask = cv2.GaussianBlur(midtone_mask, (7, 7), 0)
        
        # Float conversion
        shadow_mask = shadow_mask.astype(np.float32) / 255.0
        midtone_mask = midtone_mask.astype(np.float32) / 255.0
        
        # Apply variation based on tone
        # Less in shadows, more in midtones
        shadow_variation = (shadow_mask * combined_noise * 0.3).astype(np.uint8)
        midtone_variation = (midtone_mask * combined_noise * 0.7).astype(np.uint8)
        
        # Apply variations
        result = sketch_on_paper.copy()
        result = cv2.add(result, shadow_variation)
        result = cv2.add(result, midtone_variation)
        
        # Step 13: Final touch-ups
        # Ensure deep blacks stay deep
        _, result = cv2.threshold(result, 15, 15, cv2.THRESH_TRUNC)
        
        # Apply subtle, natural sharpening using unsharp mask
        gaussian = cv2.GaussianBlur(result, (0, 0), 2.0)
        result = cv2.addWeighted(result, 1.3, gaussian, -0.3, 0)
        
        # Final noise smoothing with bilateral filter to preserve edges
        result = cv2.bilateralFilter(result, 5, 15, 15)
        
    except Exception as e:
        print(f"Error in authentic pencil sketch V2: {str(e)}")
        raise
    
    # Add watermark if required
    if add_watermark:
        # Convert OpenCV image to PIL format for adding watermark
        pil_img = Image.fromarray(result)
        draw = ImageDraw.Draw(pil_img)
        
        # Set font for watermark
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            # If arial is not available, use default
            font = ImageFont.load_default()
            
        # Add watermark text
        watermark_text = "DRAW AI"
        img_width, img_height = pil_img.size
        
        # Calculate position (bottom-right corner)
        try:
            # For newer versions of Pillow
            if hasattr(font, "getbbox"):  
                bbox = font.getbbox(watermark_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:  
                # Fallback to deprecated method for older Pillow versions
                text_width, text_height = draw.textsize(watermark_text, font=font)
                
            margin = 20  # Margin from the edge
            x = img_width - text_width - margin
            y = img_height - text_height - margin
            
            # Add a semi-transparent background for the watermark
            draw.rectangle(
                [(x - 10, y - 10), (x + text_width + 10, y + text_height + 10)], 
                fill=(0, 0, 0, 128)
            )
            
            # Add the watermark text - removed alpha to fix issue
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255))
            
            # Convert back to OpenCV format
            result = np.array(pil_img)
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            # Continue without watermark if method fails
            result = np.array(pil_img)
    
    # Create a unique filename for the output
    output_filename = f"sketch_{uuid.uuid4().hex}.jpg"
    
    # Get the base directory of the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "temp")
    output_path = os.path.join(temp_dir, output_filename)
    
    # Ensure the temp directory exists
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Saving authentic pencil sketch to: {output_path}")
    # Save the sketch with high quality
    cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 99])
    
    return output_path
