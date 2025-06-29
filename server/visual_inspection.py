import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from improved_sketch import convert_to_authentic_pencil_sketch

def visual_inspection():
    """
    Create a visual inspection report for the updated authentic pencil sketch
    algorithm to confirm elimination of circular/square artifacts
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    results_dir = os.path.join(base_dir, 'visual_inspection')
    os.makedirs(results_dir, exist_ok=True)
    
    # Get one image for detailed inspection
    image_files = [f for f in os.listdir(uploads_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                  
    if not image_files:
        print("No test images found")
        return
    
    # Choose a diverse set of images if available
    test_images = []
    if len(image_files) >= 3:
        # Try to get different types
        for i in range(min(3, len(image_files))):
            test_images.append(os.path.join(uploads_dir, image_files[i]))
    else:
        test_images = [os.path.join(uploads_dir, image_files[0])]
    
    for index, img_path in enumerate(test_images):
        print(f"\nProcessing image {index + 1}/{len(test_images)}: {os.path.basename(img_path)}")
        
        # Generate sketch
        sketch_path = convert_to_authentic_pencil_sketch(img_path, add_watermark=False)
        print(f"Sketch generated: {os.path.basename(sketch_path)}")
        
        # Load the sketch
        sketch = cv2.imread(sketch_path)
        if sketch is None:
            print(f"Failed to load sketch: {sketch_path}")
            continue
        
        # Convert to RGB for matplotlib
        sketch_rgb = cv2.cvtColor(sketch, cv2.COLOR_BGR2RGB)
        
        # Create report figure with multiple views to check for artifacts
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle(f"Artifact Inspection - {os.path.basename(img_path)}", fontsize=16)
        
        # Full sketch
        ax1 = plt.subplot(2, 2, 1)
        ax1.imshow(sketch_rgb)
        ax1.set_title("Full Sketch")
        ax1.axis('off')
        
        # Zoomed in region to check for patterns
        h, w = sketch.shape[:2]
        zoom_region = sketch_rgb[h//3:2*h//3, w//3:2*w//3]
        ax2 = plt.subplot(2, 2, 2)
        ax2.imshow(zoom_region)
        ax2.set_title("Zoomed Region (1/3 to 2/3)")
        ax2.axis('off')
        
        # FFT to check for repeating patterns
        gray = cv2.cvtColor(sketch, cv2.COLOR_BGR2GRAY)
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = 20 * np.log(np.abs(f_shift) + 1)
        
        # Normalize for display
        magnitude_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        ax3 = plt.subplot(2, 2, 3)
        ax3.imshow(magnitude_norm, cmap='viridis')
        ax3.set_title("FFT Magnitude Spectrum (circular patterns = artifacts)")
        ax3.axis('off')
        
        # Edge detection to reveal potential artifacts
        edges = cv2.Canny(gray, 50, 150)
        ax4 = plt.subplot(2, 2, 4)
        ax4.imshow(edges, cmap='gray')
        ax4.set_title("Edge Detection (regular grid patterns = artifacts)")
        ax4.axis('off')
        
        # Save the report
        report_path = os.path.join(results_dir, f"artifact_report_{index + 1}.png")
        plt.tight_layout()
        plt.savefig(report_path)
        print(f"Inspection report saved to: {report_path}")
        
        # Open the report
        os.startfile(report_path)

if __name__ == "__main__":
    visual_inspection()
