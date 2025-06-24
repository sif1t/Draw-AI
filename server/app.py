import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sketch
import payments
from werkzeug.utils import secure_filename
import uuid
import json

app = Flask(__name__)
CORS(app)

# Configure file upload settings
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Set up upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Draw AI API is running"})

@app.route('/api/convert', methods=['POST'])
def convert_image():
    """
    Endpoint to convert an uploaded image to a pencil sketch
    """
    # Check if image is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Check if file type is allowed
    if file and allowed_file(file.filename):
        # Generate a secure filename to prevent path traversal attacks
        filename = secure_filename(file.filename)
        # Add a UUID to make it unique
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        # Convert to sketch with watermark
        try:
            sketch_path = sketch.convert_to_sketch(filepath, add_watermark=True)
            sketch_base64 = sketch.convert_to_base64(sketch_path)
            
            # Store original path for premium conversion
            session_id = uuid.uuid4().hex
            session_data = {
                "original_path": filepath,
                "sketch_path": sketch_path,
                "paid": False
            }
            
            # Save session data to temporary file
            with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'w') as f:
                json.dump(session_data, f)
            
            return jsonify({
                "success": True,
                "sketch": sketch_base64,
                "session_id": session_id
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout():
    """
    Create a Stripe checkout session for premium download
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        
        # Validate session ID
        if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
            return jsonify({"error": "Invalid session ID"}), 400
        
        # Create success and cancel URLs
        success_url = f"{request.host_url}api/payment-success?session_id={session_id}"
        cancel_url = f"{request.host_url}api/payment-cancel?session_id={session_id}"
        
        # Create Stripe checkout session
        checkout_session = payments.create_checkout_session(
            # Replace with your actual price ID from Stripe dashboard
            price_id="price_1234567890",
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return jsonify(checkout_session)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment-success', methods=['GET'])
def payment_success():
    """
    Handle successful payment and generate premium sketch
    """
    session_id = request.args.get('session_id')
    payment_intent = request.args.get('payment_intent')
    
    # Validate session ID
    if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
        return jsonify({"error": "Invalid session ID"}), 400
    
    # Verify payment (in a real app, you would verify with Stripe)
    if payment_intent:
        payment_verified = payments.verify_payment_intent(payment_intent)
        if not payment_verified:
            return jsonify({"error": "Payment verification failed"}), 400
    
    # Get session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # Convert to sketch without watermark
    try:
        premium_sketch_path = sketch.convert_to_sketch(
            session_data["original_path"], 
            add_watermark=False
        )
        
        # Update session data
        session_data["premium_sketch_path"] = premium_sketch_path
        session_data["paid"] = True
        
        # Save updated session data
        with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'w') as f:
            json.dump(session_data, f)
        
        premium_sketch_base64 = sketch.convert_to_base64(premium_sketch_path)
        
        return jsonify({
            "success": True,
            "premium_sketch": premium_sketch_base64,
            "download_url": f"/api/download/{session_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment-cancel', methods=['GET'])
def payment_cancel():
    """
    Handle cancelled payment
    """
    return jsonify({
        "success": False,
        "message": "Payment was cancelled"
    })

@app.route('/api/download/<session_id>', methods=['GET'])
def download_sketch(session_id):
    """
    Download the premium sketch
    """
    # Validate session ID
    if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
        return jsonify({"error": "Invalid session ID"}), 400
    
    # Get session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # Check if premium sketch exists and is paid for
    if not session_data.get("paid") or not os.path.exists(session_data.get("premium_sketch_path", "")):
        return jsonify({"error": "Premium sketch not available"}), 403
    
    # Send the file for download
    return send_file(
        session_data["premium_sketch_path"],
        as_attachment=True,
        download_name="premium_sketch.jpg",
        mimetype='image/jpeg'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
