import os
import sys
import cv2
import numpy as np
from improved_sketch import convert_to_authentic_pencil_sketch

def analyze_artifacts(image_path):
    """
    Analyze an image for circular or square pattern artifacts
    by checking for repeating patterns in the frequency domain
    """
    # Read the image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error loading image {image_path}")
        return False
        
    # Apply FFT to detect repeating patterns
    f_transform = np.fft.fft2(img)
    f_shift = np.fft.fftshift(f_transform)
    magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
    
    # Check for strong frequency components that would indicate patterns
    # (simplified - just check variance in high frequency areas)
    h, w = magnitude_spectrum.shape
    center_h, center_w = h//2, w//2
    
    # Extract regions away from DC component (low frequency center)
    margin = 20
    high_freq_regions = [
        magnitude_spectrum[margin:center_h-margin, margin:center_w-margin],  # Top-left
        magnitude_spectrum[margin:center_h-margin, center_w+margin:w-margin],  # Top-right
        magnitude_spectrum[center_h+margin:h-margin, margin:center_w-margin],  # Bottom-left
        magnitude_spectrum[center_h+margin:h-margin, center_w+margin:w-margin]  # Bottom-right
    ]
    
    # Check if there are strong peaks in high frequency areas
    # which would suggest repeating patterns
    for region in high_freq_regions:
        max_val = np.max(region)
        mean_val = np.mean(region)
        # If there are sharp peaks (much higher than mean), likely artifact patterns
        if max_val > mean_val * 2:
            return True
            
    return False

def test_for_circular_artifacts():
    """
    Test the authentic pencil sketch for circular/square artifacts
    on multiple test images
    """
    # Get the base directory and create test directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    results_dir = os.path.join(base_dir, 'test_results')
    
    # Ensure directories exist
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    # Get all images in the uploads directory
    image_files = [f for f in os.listdir(uploads_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("No test images found in the uploads directory.")
        print("Please place at least one image in the uploads directory.")
        return
    
    # Limit to 5 images maximum for testing
    image_files = image_files[:5]
    print(f"Testing {len(image_files)} images for circular/square artifacts...")
    
    # Test each image
    artifacts_detected = 0
    for image_file in image_files:
        test_image = os.path.join(uploads_dir, image_file)
        print(f"\nTesting image: {image_file}")
        
        try:
            # Generate sketch
            sketch_path = convert_to_authentic_pencil_sketch(test_image, add_watermark=False)
            
            # Analyze for artifacts
            has_artifacts = analyze_artifacts(sketch_path)
            
            # Report results
            if has_artifacts:
                artifacts_detected += 1
                print(f"❌ Potential artifacts detected in: {os.path.basename(sketch_path)}")
            else:
                print(f"✅ No artifacts detected in: {os.path.basename(sketch_path)}")
                
            # Save to results for visual inspection
            result_path = os.path.join(results_dir, f"artifact_test_{os.path.basename(sketch_path)}")
            os.rename(sketch_path, result_path)
            print(f"   Saved result to: {result_path}")
            
            # Open the image for visual inspection
            os.startfile(result_path)
            
        except Exception as e:
            print(f"❌ Error processing {image_file}: {str(e)}")
    
    # Final summary
    if artifacts_detected == 0:
        print("\n✅ SUCCESS: No circular/square artifacts detected in any test images!")
    else:
        print(f"\n❌ ATTENTION: Potential artifacts detected in {artifacts_detected} out of {len(image_files)} images.")

if __name__ == "__main__":
    test_for_circular_artifacts()
