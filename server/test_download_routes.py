import requests
import os
import json
import sys
import base64
from PIL import Image
import io

def test_download_routes():
    """
    Test the download routes functionality
    """
    base_url = "http://localhost:5000"
    
    # Path to store test files
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    # Step 1: Create a test session by uploading an image
    # Find an image in uploads directory
    uploads_dir = "uploads"
    image_path = None
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(uploads_dir, filename)
            break
    
    if not image_path:
        print("Error: No test image found in uploads directory")
        return
    
    print(f"Found test image: {image_path}")
    
    # Upload the image
    with open(image_path, 'rb') as img_file:
        print("\n1. Testing image upload with style...")
        files = {'image': (os.path.basename(image_path), img_file, 'image/jpeg')}
        data = {'style': 'ultra-clear'}
        response = requests.post(f"{base_url}/api/convert/style", files=files, data=data)
        
        if response.status_code != 200:
            print(f"Error uploading image: {response.status_code}")
            print(response.text)
            return
            
        upload_data = response.json()
        session_id = upload_data.get("session_id")
        
        if not session_id:
            print("Error: No session ID returned")
            return
            
        print(f"Upload successful! Session ID: {session_id}")
    
    # Step 2: Test the free download route
    print("\n2. Testing free download route...")
    response = requests.get(f"{base_url}/api/download/free/{session_id}")
    
    if response.status_code == 200:
        # Save the downloaded image
        free_output_path = os.path.join(download_dir, f"free_watermarked_{session_id}.jpg")
        with open(free_output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Free download successful! Saved to: {free_output_path}")
    else:
        print(f"✗ Free download failed: {response.status_code}")
        print(response.text)
        
    # Step 3: Simulate a successful payment - normally done through Stripe
    # For testing, we'll create a fake premium conversion
    print("\n3. Testing premium sketch route...")
    response = requests.get(f"{base_url}/api/get-premium-sketch?session_id={session_id}")
    
    if response.status_code == 200:
        payment_data = response.json()
        premium_base64 = payment_data.get("premium_sketch")
        download_url = payment_data.get("download_url")
        
        print(f"✓ Payment success route working")
        print(f"  Download URL: {download_url}")
        
        # Save the premium preview image
        if premium_base64:
            premium_preview_path = os.path.join(download_dir, f"premium_preview_{session_id}.jpg")
            
            try:
                image_data = base64.b64decode(premium_base64)
                with open(premium_preview_path, "wb") as f:
                    f.write(image_data)
                print(f"  Premium preview saved to: {premium_preview_path}")
            except Exception as e:
                print(f"  Error saving premium preview: {str(e)}")
    else:
        print(f"✗ Payment success route failed: {response.status_code}")
        print(response.text)
    
    # Step 4: Test premium download route
    print("\n4. Testing premium download route...")
    response = requests.get(f"{base_url}{download_url}")
    
    if response.status_code == 200:
        # Save the downloaded premium image
        premium_output_path = os.path.join(download_dir, f"premium_no_watermark_{session_id}.jpg")
        with open(premium_output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Premium download successful! Saved to: {premium_output_path}")
        print("\nCompare the free and premium versions to verify:")
        print(f"  Free version (with watermark): {free_output_path}")
        print(f"  Premium version (no watermark): {premium_output_path}")
    else:
        print(f"✗ Premium download failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Testing download routes...")
    test_download_routes()
