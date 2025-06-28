import os
import sys
import requests
import json
from PIL import Image, ImageTk
import io
import base64
import uuid
import time
import argparse

# Test configuration
API_BASE = "http://localhost:5000"

def test_flask_api_styles():
    """
    Test all sketch styles through the Flask API
    """
    print("\n=== Testing Flask API for All Sketch Styles ===\n")
    
    # Get the base directory and image paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    
    # Get a test image
    image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        print("Error: No test images found in the uploads directory")
        return False
    
    test_image_path = os.path.join(uploads_dir, image_files[0])
    print(f"Using test image: {test_image_path}")
    
    # All styles to test
    styles = ['pencil', 'realistic', 'portrait', 'ultra-clear', 'authentic-pencil']
    results = {}
    
    try:
        for style in styles:
            print(f"\nTesting '{style}' style...")
            
            # Create form data with the image and style
            with open(test_image_path, 'rb') as img_file:
                files = {'image': (image_files[0], img_file, 'image/jpeg')}
                data = {'style': style}
                
                # Make API request
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE}/api/convert/style", 
                    files=files, 
                    data=data,
                    timeout=30
                )
                elapsed_time = time.time() - start_time
                
                # Process response
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        session_id = result.get('session_id')
                        sketch_base64 = result.get('sketch')
                        
                        # Save the sketch image
                        if sketch_base64:
                            # Create output directory
                            output_dir = os.path.join(base_dir, 'test_output')
                            os.makedirs(output_dir, exist_ok=True)
                            
                            # Save base64 image to file
                            image_data = base64.b64decode(sketch_base64)
                            output_path = os.path.join(output_dir, f"api_test_{style}_{uuid.uuid4().hex[:6]}.jpg")
                            
                            with open(output_path, 'wb') as out_file:
                                out_file.write(image_data)
                                
                            results[style] = {
                                'status': 'Success',
                                'path': output_path,
                                'time': f"{elapsed_time:.2f}s",
                                'session_id': session_id
                            }
                            
                            print(f"  ✓ Success! Sketch saved to: {output_path}")
                            print(f"  - Processing time: {elapsed_time:.2f} seconds")
                            
                            # Optionally open the image on Windows
                            if os.name == 'nt':
                                os.startfile(output_path)
                        else:
                            print(f"  ✗ Error: No sketch data in response")
                            results[style] = {'status': 'Error - No sketch data'}
                    else:
                        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
                        results[style] = {'status': f"Error - {result.get('error', 'Unknown error')}"}
                else:
                    print(f"  ✗ HTTP Error: {response.status_code} - {response.text}")
                    results[style] = {'status': f"HTTP Error {response.status_code}"}
        
        # Summary report
        print("\n=== Test Results Summary ===")
        for style, result in results.items():
            status = result.get('status')
            time_taken = result.get('time', 'N/A')
            session_id = result.get('session_id', 'N/A')
            path = result.get('path', 'N/A')
            
            print(f"Style: {style}")
            print(f"  Status: {status}")
            print(f"  Time: {time_taken}")
            
            if 'Success' in status:
                print(f"  Session ID: {session_id}")
                print(f"  Output: {path}")
            print()
            
        # Overall result
        success_count = sum(1 for r in results.values() if r.get('status', '').startswith('Success'))
        print(f"Overall: {success_count}/{len(styles)} styles completed successfully")
        return success_count == len(styles)
                
    except Exception as e:
        print(f"Test error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test Draw AI sketch styles via the Flask API')
    args = parser.parse_args()
    
    # Make sure Flask server is running
    try:
        health_check = requests.get(f"{API_BASE}/api/health", timeout=2)
        if health_check.status_code != 200:
            print(f"Error: Flask server is not responding correctly. Status: {health_check.status_code}")
            return 1
    except Exception as e:
        print(f"Error: Flask server is not running at {API_BASE}. Please start the Flask server first.")
        print(f"Error details: {str(e)}")
        return 1
    
    # Run the tests
    success = test_flask_api_styles()
    
    if success:
        print("\nAll API tests completed successfully!")
        return 0
    else:
        print("\nSome API tests failed. Please check the logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
