import base64
import os
import json
import requests
from io import BytesIO
from PIL import Image

def save_attachment_image(filename):
    """Save the attachment image to a file"""
    # Create a directory to save the image
    os.makedirs("uploads", exist_ok=True)
    
    # Save the attached image from the chat (this would be replaced with actual code to access the attachment)
    # For demonstration purposes, let's assume we have a placeholder
    with open(filename, 'wb') as f:
        # This is where you would write the actual image data
        f.write(b'PLACEHOLDER')
    
    return filename

def upload_to_draw_ai(image_path):
    """Upload an image to the Draw AI API"""
    url = 'http://localhost:5000/api/convert'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
    
    return response.json()

def save_session_data(session_id, original_path):
    """Save mock session data for testing"""
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    session_data = {
        "original_path": original_path,
        "sketch_path": os.path.join("temp", f"sketch_{session_id}.jpg"),
        "paid": False
    }
    
    with open(os.path.join(temp_dir, f"{session_id}.json"), 'w') as f:
        json.dump(session_data, f)
    
    return session_id

def main():
    """Main function to test the Draw AI watermark"""
    # Step 1: Create a test image
    test_image_path = os.path.join("uploads", "test_image.jpg")
    
    # For real testing, we'd upload the provided attachment
    # Here, we'll create a simple test image using PIL
    image = Image.new('RGB', (800, 600), color='white')
    image.save(test_image_path)
    print(f"Created test image at {test_image_path}")
    
    # Step 2: Create a mock session
    session_id = "test123"
    save_session_data(session_id, os.path.abspath(test_image_path))
    print(f"Created mock session with ID: {session_id}")
    
    # Step 3: Print URL for testing
    print("\nTo test the watermarked image download, open this URL in your browser:")
    print(f"http://localhost:5000/api/download/free/{session_id}")

if __name__ == "__main__":
    main()
