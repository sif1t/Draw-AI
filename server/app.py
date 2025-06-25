import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sketch
import payments
from werkzeug.utils import secure_filename
import uuid
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes with more permissive settings
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configure file upload settings with absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

print(f"Upload folder: {UPLOAD_FOLDER}")
print(f"Temp folder: {TEMP_FOLDER}")

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
            # Print file path for debugging
            print(f"Processing file: {filepath}")
            print(f"File exists: {os.path.exists(filepath)}")
            
            sketch_path = sketch.convert_to_sketch(filepath, add_watermark=True)
            print(f"Generated sketch at: {sketch_path}")
            print(f"Sketch exists: {os.path.exists(sketch_path)}")
            
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
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in image conversion: {str(e)}")
            print(error_details)
            return jsonify({"error": str(e), "details": error_details}), 500
    
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
        
        # Create success and cancel URLs with frontend redirect
        # These URLs should point to your frontend app, not the backend API
        frontend_url = request.headers.get('Origin', 'http://localhost:3000')
        success_url = f"{frontend_url}/result?payment_status=success&session_id={session_id}"
        cancel_url = f"{frontend_url}/result?payment_status=cancelled&session_id={session_id}"
        
        # Create Stripe checkout session
        checkout_session = payments.create_checkout_session(
            # Get price ID from environment variable
            price_id=os.getenv('STRIPE_PRICE_ID'),
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return jsonify(checkout_session)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating checkout session: {str(e)}")
        print(error_details)
        
        # Check for common Stripe errors
        error_msg = str(e)
        if "API key" in error_msg:
            return jsonify({"error": "Payment system configuration error. Please check Stripe API keys."}), 500
        
        return jsonify({"error": error_msg, "details": error_details}), 500

@app.route('/api/payment-success', methods=['GET', 'POST'])
def payment_success():
    """
    Handle successful payment and generate premium sketch
    """
    # Handle both GET and POST requests
    if request.method == 'GET':
        session_id = request.args.get('session_id')
        payment_intent = request.args.get('payment_intent')
    else:
        data = request.json
        session_id = data.get('session_id')
        payment_intent = data.get('payment_intent')
    
    # Debug output
    print(f"Payment success request received - Session ID: {session_id}, Payment Intent: {payment_intent}")
    
    # Validate session ID
    if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
        return jsonify({"error": "Invalid session ID"}), 400
    
    # Get session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # If already paid, return existing premium sketch
    if session_data.get("paid") and os.path.exists(session_data.get("premium_sketch_path", "")):
        premium_sketch_base64 = sketch.convert_to_base64(session_data["premium_sketch_path"])
        return jsonify({
            "success": True,
            "premium_sketch": premium_sketch_base64,
            "download_url": f"/api/download/{session_id}"
        })
    
    # Verify payment with our local payment system
    payment_verified = True
    
    # For our local system, the payment ID is stored in session_id parameter
    if session_id:
        payment_verified = payments.verify_payment_intent(session_id)
        if not payment_verified:
            return jsonify({"error": "Payment verification failed. Please complete the payment process."}), 400
    
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

@app.route('/api/download/free/<session_id>', methods=['GET'])
def download_free_sketch(session_id):
    """
    Download the free sketch with watermark
    """
    # Validate session ID
    if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
        return jsonify({"error": "Invalid session ID"}), 400
    
    # Get session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # Send the free version (with watermark) for download
    if os.path.exists(session_data.get("sketch_path", "")):
        return send_file(
            session_data["sketch_path"],
            as_attachment=True,
            download_name="draw_ai_free_sketch.jpg",
            mimetype='image/jpeg'
        )
    else:
        return jsonify({"error": "Sketch file not found"}), 404

@app.route('/api/download/<session_id>', methods=['GET'])
def download_sketch(session_id):
    """
    Download the sketch (premium or free with watermark)
    """
    # Validate session ID
    if not session_id or not os.path.exists(os.path.join(TEMP_FOLDER, f"{session_id}.json")):
        return jsonify({"error": "Invalid session ID"}), 400
    
    # Get session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # Check if this is a premium (paid) download
    if session_data.get("paid") and os.path.exists(session_data.get("premium_sketch_path", "")):
        # Send the premium file for download
        return send_file(
            session_data["premium_sketch_path"],
            as_attachment=True,
            download_name="premium_sketch.jpg",
            mimetype='image/jpeg'
        )
    else:
        # Send the free version (with watermark) for download
        if os.path.exists(session_data.get("sketch_path", "")):
            return send_file(
                session_data["sketch_path"],
                as_attachment=True,
                download_name="free_sketch.jpg",
                mimetype='image/jpeg'
            )
        else:
            return jsonify({"error": "Sketch file not found"}), 404

# Creating a new route for payment checkout page
@app.route('/payment/checkout', methods=['GET'])
def payment_checkout():
    """
    Render a simple payment form for the local payment system
    """
    payment_id = request.args.get('payment_id')
    
    # Return HTML for a simple payment form
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Draw AI - Payment</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 15px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            button {{ background-color: #ff5c38; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }}
            button:hover {{ background-color: #e64a2e; }}
            .note {{ font-size: 12px; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Draw AI - Payment</h1>
            <p>Complete your purchase to remove the watermark</p>
            <form id="payment-form" action="/payment/process" method="post">
                <input type="hidden" name="payment_id" value="{payment_id}">
                
                <div class="form-group">
                    <label for="card-number">Card Number</label>
                    <input type="text" id="card-number" name="card_number" placeholder="1234 5678 9012 3456" maxlength="16" required>
                </div>
                
                <div class="form-group">
                    <label for="expiry">Expiration Date</label>
                    <input type="text" id="expiry" name="expiry" placeholder="MM/YY" maxlength="5" required>
                </div>
                
                <div class="form-group">
                    <label for="cvc">CVC</label>
                    <input type="text" id="cvc" name="cvc" placeholder="123" maxlength="3" required>
                </div>
                
                <button type="submit">Pay $1.00</button>
                
                <div class="note">
                    <p>This is a test payment system. Use card number ending in 4242 to simulate successful payment.</p>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/payment/process', methods=['POST'])
def process_payment():
    """
    Process the payment form submission
    """
    payment_id = request.form.get('payment_id')
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvc = request.form.get('cvc')
    
    # Basic validation
    if not all([payment_id, card_number, expiry, cvc]):
        return jsonify({"error": "Missing payment information"}), 400
    
    # Process payment
    result = payments.process_payment(payment_id, card_number, expiry, cvc)
    
    if result['success']:
        # Redirect to success URL
        return f"""
        <html>
        <head>
            <title>Payment Successful</title>
            <script>
                window.location.href = "{result['redirect_url']}";
            </script>
        </head>
        <body>
            <h1>Payment Successful</h1>
            <p>Redirecting to download page...</p>
        </body>
        </html>
        """
    else:
        # Redirect to cancel URL with error
        return f"""
        <html>
        <head>
            <title>Payment Failed</title>
            <script>
                window.location.href = "{result['redirect_url']}";
            </script>
        </head>
        <body>
            <h1>Payment Failed</h1>
            <p>Error: {result.get('error', 'Unknown error')}</p>
            <p>Redirecting...</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
