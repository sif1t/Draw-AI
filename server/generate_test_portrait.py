import os
import cv2
import numpy as np
import random

def create_test_image():
    """Creates a simple test face image for portrait testing"""
    # Create directory for test images
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_images")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a basic gradient test image
    test_img = np.zeros((800, 600, 3), dtype=np.uint8)
    
    # Add background gradient
    for i in range(800):
        for j in range(600):
            value = 120 + i // 10  # Gradient from top to bottom
            test_img[i, j] = [value, value + 10, value + 20]  # RGB gradient
    
    # Add face
    center_x, center_y = 300, 350
    radius = 180
    cv2.circle(test_img, (center_x, center_y), radius, (213, 182, 165), -1)  # Face
    
    # Add facial features
    # Eyes
    cv2.ellipse(test_img, (center_x - 60, center_y - 40), (25, 15), 0, 0, 360, (255, 255, 255), -1)  # Left eye white
    cv2.ellipse(test_img, (center_x + 60, center_y - 40), (25, 15), 0, 0, 360, (255, 255, 255), -1)  # Right eye white
    
    cv2.circle(test_img, (center_x - 60, center_y - 40), 10, (50, 80, 120), -1)  # Left iris
    cv2.circle(test_img, (center_x + 60, center_y - 40), 10, (50, 80, 120), -1)  # Right iris
    
    cv2.circle(test_img, (center_x - 60, center_y - 40), 5, (0, 0, 0), -1)  # Left pupil
    cv2.circle(test_img, (center_x + 60, center_y - 40), 5, (0, 0, 0), -1)  # Right pupil
    
    # Eyebrows
    cv2.line(test_img, (center_x - 90, center_y - 70), (center_x - 30, center_y - 60), (60, 50, 40), 5)  # Left eyebrow
    cv2.line(test_img, (center_x + 30, center_y - 60), (center_x + 90, center_y - 70), (60, 50, 40), 5)  # Right eyebrow
    
    # Nose
    cv2.line(test_img, (center_x, center_y - 40), (center_x, center_y + 20), (180, 150, 140), 3)  # Bridge
    cv2.ellipse(test_img, (center_x, center_y + 20), (20, 10), 0, 0, 180, (180, 150, 140), -1)  # Nostrils
    
    # Mouth
    cv2.ellipse(test_img, (center_x, center_y + 70), (60, 20), 0, 0, 180, (150, 90, 90), -1)  # Lips
    
    # Hair
    # Create random hair strands
    for _ in range(300):
        x = random.randint(center_x - 150, center_x + 150)
        y = random.randint(center_y - 220, center_y - 120)
        length = random.randint(30, 100)
        angle = random.uniform(-0.5, 0.5)  # Random angle variation
        
        end_x = int(x + length * np.cos(angle))
        end_y = int(y + length * np.sin(angle))
        
        # Only draw hair if near the top of the head
        if y < center_y - 70:
            cv2.line(test_img, (x, y), (end_x, end_y), (60, 40, 30), 1)
    
    # Add some shadows and highlights to make it more realistic
    cv2.ellipse(test_img, (center_x - 50, center_y + 60), (80, 60), 30, 0, 360, (190, 160, 145), -1)  # Left cheek
    cv2.ellipse(test_img, (center_x + 50, center_y + 60), (80, 60), 330, 0, 360, (190, 160, 145), -1)  # Right cheek
    
    # Save the test image
    test_image_path = os.path.join(test_dir, "test_face.jpg")
    cv2.imwrite(test_image_path, test_img)
    print(f"Created test image at: {test_image_path}")
    
    return test_image_path

if __name__ == "__main__":
    test_image_path = create_test_image()
    
    # Test the generated image with the enhanced portrait sketch
    from enhanced_realistic_portrait_sketch import convert_to_realistic_portrait_sketch
    
    sketch_path = convert_to_realistic_portrait_sketch(test_image_path, add_watermark=False)
    print(f"Generated enhanced portrait sketch saved to: {sketch_path}")
    
    # Save a copy to a more accessible location for viewing
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portrait_results")
    os.makedirs(result_dir, exist_ok=True)
    
    # Read the sketch and save a copy
    sketch = cv2.imread(sketch_path)
    if sketch is not None:
        result_path = os.path.join(result_dir, "enhanced_portrait_test_face.jpg")
        cv2.imwrite(result_path, sketch)
        
        print(f"Saved copy of result to: {result_path}")
        print("Test completed successfully!")
    else:
        print(f"Failed to read the generated sketch from {sketch_path}")
