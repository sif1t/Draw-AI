import os
import sys
import json
import cv2

# Add parent directory to path to import sketch module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sketch import convert_to_sketch

# Test image path - replace with your image path
input_path = "c:\\Users\\Arifeen\\Desktop\\Draw AI\\server\\uploads\\test_input.jpg"

# Convert the image with watermark
output_path = convert_to_sketch(input_path, add_watermark=True)

print(f"Image processed and saved to: {output_path}")
print("Watermark has been applied to the image.")

# Create a test session for API testing
session_id = "test_session"
session_data = {
    "original_path": input_path,
    "sketch_path": output_path,
    "paid": False
}

# Save session data
with open(f"c:\\Users\\Arifeen\\Desktop\\Draw AI\\server\\temp\\{session_id}.json", "w") as f:
    json.dump(session_data, f)

print(f"Test session created: {session_id}")
print(f"To test the API endpoint, navigate to:")
print(f"http://localhost:5000/api/download/free/{session_id}")
