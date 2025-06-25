import requests
import os
from PIL import Image
import io

# Create a directory for downloads
download_dir = "downloads"
os.makedirs(download_dir, exist_ok=True)

# Session ID from the previous test
session_id = "test123"

# URL for downloading the free version with watermark
url = f"http://localhost:5000/api/download/free/{session_id}"

print(f"Downloading from: {url}")
response = requests.get(url)

if response.status_code == 200:
    # Save the downloaded image
    output_path = os.path.join(download_dir, "watermarked_image.jpg")
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    print(f"Image downloaded and saved to: {output_path}")
    print("The image has the 'Draw AI' watermark applied.")
else:
    print(f"Failed to download: {response.status_code}")
    print(response.text)
