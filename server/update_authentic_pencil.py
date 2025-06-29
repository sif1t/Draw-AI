import os
import sys
import cv2
import numpy as np
import shutil

def update_application():
    """
    Update the application to use the improved authentic pencil sketch algorithm
    as the default for the authentic pencil sketch style.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. First, import the new function into improved_sketch.py
    improved_sketch_path = os.path.join(base_dir, 'improved_sketch.py')
    improved_authentic_path = os.path.join(base_dir, 'improved_authentic_sketch.py')
    
    # Check if files exist
    if not os.path.exists(improved_sketch_path):
        print(f"Error: {improved_sketch_path} not found")
        return
        
    if not os.path.exists(improved_authentic_path):
        print(f"Error: {improved_authentic_path} not found")
        return
    
    print("1. Importing improved algorithm to main sketch module...")
    # Read the improved authentic sketch function
    with open(improved_authentic_path, 'r') as f:
        improved_code = f.read()
    
    # Extract the function definition
    import re
    func_match = re.search(r'def convert_to_authentic_pencil_sketch_v2\([^)]*\):(.*?)def', 
                          improved_code, re.DOTALL)
                          
    if not func_match:
        print("Error: Could not find function definition in improved_authentic_sketch.py")
        return
        
    # Get function body and rename it
    func_code = func_match.group(1)
    func_code = func_code.replace('convert_to_authentic_pencil_sketch_v2', 
                                'convert_to_authentic_pencil_sketch')
    
    # Now add it to the improved_sketch.py file
    # First create a backup
    backup_path = os.path.join(base_dir, 'improved_sketch.py.bak')
    shutil.copy2(improved_sketch_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    # Replace the existing function
    with open(improved_sketch_path, 'r') as f:
        original_code = f.read()
    
    # Find the authentic pencil sketch function
    old_func_match = re.search(r'def convert_to_authentic_pencil_sketch\([^)]*\):(.*?)def', 
                             original_code, re.DOTALL)
                             
    if not old_func_match:
        print("Error: Could not find original function in improved_sketch.py")
        return
    
    # Replace the function
    new_code = original_code.replace(old_func_match.group(0), 
                                   f"def convert_to_authentic_pencil_sketch(image_path, add_watermark=True):{func_code}def")
    
    # Write the updated code
    with open(improved_sketch_path, 'w') as f:
        f.write(new_code)
    
    print("✅ Successfully updated authentic pencil sketch algorithm!")
    print("\nRun tests to verify the changes:")
    print("1. python test_authentic_pencil_sketch.py")
    print("2. python test_all_sketch_styles.py")

if __name__ == "__main__":
    update_application()
