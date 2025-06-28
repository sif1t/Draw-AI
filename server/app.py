import os
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sketch
import improved_sketch  # Import the improved sketch module
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
            
            # Use the improved sketch implementation instead
            sketch_path = improved_sketch.convert_to_pencil_sketch(filepath, add_watermark=True)
            print(f"Generated sketch at: {sketch_path}")
            print(f"Sketch exists: {os.path.exists(sketch_path)}")
            
            sketch_base64 = improved_sketch.convert_to_base64(sketch_path)
            
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

@app.route('/api/convert/style', methods=['POST'])
def convert_image_with_style():
    """
    Endpoint to convert an uploaded image to a pencil sketch with different style options
    """
    # Check if image is in the request
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Get style parameter (default to 'pencil')
    style = request.form.get('style', 'pencil')
    
    # Check if file type is allowed
    if file and allowed_file(file.filename):
        # Generate a secure filename to prevent path traversal attacks
        filename = secure_filename(file.filename)
        # Add a UUID to make it unique
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        # Convert to sketch with watermark based on style
        try:
            print(f"Processing file: {filepath} with style: {style}")
            
            if style == 'pencil':
                sketch_path = improved_sketch.convert_to_pencil_sketch(filepath, add_watermark=True)
            elif style == 'realistic':
                sketch_path = improved_sketch.convert_to_realistic_pencil_sketch(filepath, add_watermark=True)
            elif style == 'portrait':
                sketch_path = improved_sketch.convert_to_ultra_clear_sketch(filepath, add_watermark=True)
            elif style == 'ultra-clear':
                sketch_path = improved_sketch.convert_to_ultra_clear_sketch(filepath, add_watermark=True)
            elif style == 'authentic-pencil':
                sketch_path = improved_sketch.convert_to_authentic_pencil_sketch(filepath, add_watermark=True)
            else:
                # Default to artistic portrait sketch for best results
                sketch_path = improved_sketch.convert_to_artistic_portrait_sketch(filepath, add_watermark=True)
            
            print(f"Generated sketch at: {sketch_path}")
            
            sketch_base64 = improved_sketch.convert_to_base64(sketch_path)
            
            # Store original path for premium conversion
            session_id = uuid.uuid4().hex
            session_data = {
                "original_path": filepath,
                "sketch_path": sketch_path,
                "style": style,
                "paid": False
            }
            
            # Save session data to temporary file
            with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'w') as f:
                json.dump(session_data, f)
            
            return jsonify({
                "success": True,
                "sketch": sketch_base64,
                "session_id": session_id,
                "style": style
            })
            
        except Exception as e:
            print(f"Error converting image: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

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
            "purchase_date": session_data.get("purchase_date", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "transaction_id": session_data.get("transaction_id", ""),
            "download_url": f"/api/download/{session_id}"
        })
    
    # Verify payment with our local payment system
    payment_verified = True
    
    # For our local system, the payment ID is stored in session_id parameter
    if session_id:
        payment_verified = payments.verify_payment_intent(session_id)
        if not payment_verified:
            return jsonify({
                "error": "Payment verification failed. Please complete the payment process.",
                "error_code": "payment_incomplete"
            }), 400
    
    # Get fresh session data
    with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'r') as f:
        session_data = json.load(f)
    
    # Generate transaction ID if not present
    transaction_id = session_data.get("transaction_id", f"TX{uuid.uuid4().hex[:8].upper()}")
    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Convert to sketch without watermark
    try:
        premium_sketch_path = sketch.convert_to_sketch(
            session_data["original_path"], 
            add_watermark=False
        )
        
        # Update session data with payment details
        session_data["premium_sketch_path"] = premium_sketch_path
        session_data["paid"] = True
        session_data["purchase_date"] = purchase_date
        session_data["transaction_id"] = transaction_id
        
        # Save updated session data
        with open(os.path.join(TEMP_FOLDER, f"{session_id}.json"), 'w') as f:
            json.dump(session_data, f)
        
        premium_sketch_base64 = sketch.convert_to_base64(premium_sketch_path)
        
        return jsonify({
            "success": True,
            "premium_sketch": premium_sketch_base64,
            "purchase_date": purchase_date,
            "transaction_id": transaction_id,
            "download_url": f"/api/download/{session_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-premium-sketch', methods=['GET'])
def get_premium_sketch():
    """
    Endpoint to retrieve premium sketch without watermark (renamed to avoid conflict)
    """
    try:
        # Get session ID from query parameters
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({"error": "No session ID provided"}), 400
            
        # Check if session data exists
        session_file = os.path.join(TEMP_FOLDER, f"{session_id}.json")
        if not os.path.exists(session_file):
            return jsonify({"error": "Invalid session ID"}), 400
            
        # Load session data
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Mark as paid in session data
        session_data["paid"] = True
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Get the original image path
        original_path = session_data.get("original_path")
        if not original_path or not os.path.exists(original_path):
            return jsonify({"error": "Original image not found"}), 404
        
        # Get the style
        style = session_data.get("style", "pencil")
        
        # Generate a premium sketch without watermark
        try:
            print(f"Generating premium sketch without watermark for style: {style}")
            
            # Use the original style for the premium version
            if style == 'pencil':
                premium_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=False)
            elif style == 'realistic':
                premium_path = improved_sketch.convert_to_realistic_pencil_sketch(original_path, add_watermark=False)
            elif style == 'portrait':
                premium_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=False)
            elif style == 'ultra-clear':
                premium_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=False)
            elif style == 'authentic-pencil':
                premium_path = improved_sketch.convert_to_authentic_pencil_sketch(original_path, add_watermark=False)
            else:
                premium_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=False)
                
            print(f"Generated premium sketch at: {premium_path}")
            
            # Store the premium path in session data
            session_data["premium_path"] = premium_path
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            
            # Convert to base64 for preview
            premium_base64 = improved_sketch.convert_to_base64(premium_path)
            
            # Create a download URL
            download_url = f"/api/download/premium/{session_id}"
            
            return jsonify({
                "success": True,
                "premium_sketch": premium_base64,
                "download_url": download_url
            })
            
        except Exception as e:
            print(f"Error generating premium sketch: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        print(f"Error during payment success: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/premium/<session_id>', methods=['GET'])
def download_premium_sketch(session_id):
    """
    Endpoint to download the premium version without watermark
    """
    try:
        # Check if session data exists
        session_file = os.path.join(TEMP_FOLDER, f"{session_id}.json")
        if not os.path.exists(session_file):
            return jsonify({"error": "Invalid session ID"}), 400
            
        # Load session data
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Check if payment was made
        if not session_data.get("paid", False):
            return jsonify({"error": "Payment required"}), 402
        
        # Get the premium sketch path
        premium_path = session_data.get("premium_path")
        if not premium_path or not os.path.exists(premium_path):
            # If premium path is not found, regenerate it
            original_path = session_data.get("original_path")
            style = session_data.get("style", "pencil")
            
            if not original_path or not os.path.exists(original_path):
                return jsonify({"error": "Original image not found"}), 404
                
            print(f"Re-generating premium sketch for style: {style}")
            
            if style == 'pencil':
                premium_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=False)
            elif style == 'realistic':
                premium_path = improved_sketch.convert_to_realistic_pencil_sketch(original_path, add_watermark=False)
            elif style == 'portrait':
                premium_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=False)
            elif style == 'ultra-clear':
                premium_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=False)
            elif style == 'authentic-pencil':
                premium_path = improved_sketch.convert_to_authentic_pencil_sketch(original_path, add_watermark=False)
            else:
                premium_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=False)
                
            # Update session data with premium path
            session_data["premium_path"] = premium_path
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
        
        # Set a better filename for the download
        style = session_data.get("style", "pencil")
        download_filename = f"Draw_AI_Premium_{style}_{session_id[:8]}.jpg"
        
        # Return the file for download
        return send_file(
            premium_path,
            as_attachment=True,
            download_name=download_filename,
            mimetype='image/jpeg'
        )
        
    except Exception as e:
        print(f"Error during premium sketch download: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/free/<session_id>', methods=['GET'])
def download_free_sketch(session_id):
    """
    Endpoint to download the free version with the Draw AI watermark
    """
    try:
        # Check if session data exists
        session_file = os.path.join(TEMP_FOLDER, f"{session_id}.json")
        if not os.path.exists(session_file):
            return jsonify({"error": "Invalid session ID"}), 400
            
        # Load session data
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Get the sketch path
        sketch_path = session_data.get("sketch_path")
        if not sketch_path or not os.path.exists(sketch_path):
            return jsonify({"error": "Sketch file not found"}), 404
            
        # Get the original style used
        style = session_data.get("style", "pencil")
        
        # Get the original image path
        original_path = session_data.get("original_path")
        if not original_path or not os.path.exists(original_path):
            return jsonify({"error": "Original image not found"}), 404
        
        # Generate a new sketch with proper Draw AI watermark to ensure consistency
        try:
            print(f"Re-generating watermarked sketch for download with style: {style}")
            
            # Use the original style for the download
            if style == 'pencil':
                download_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=True)
            elif style == 'realistic':
                download_path = improved_sketch.convert_to_realistic_pencil_sketch(original_path, add_watermark=True)
            elif style == 'portrait':
                download_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=True)
            elif style == 'ultra-clear':
                download_path = improved_sketch.convert_to_ultra_clear_sketch(original_path, add_watermark=True)
            elif style == 'authentic-pencil':
                download_path = improved_sketch.convert_to_authentic_pencil_sketch(original_path, add_watermark=True)
            else:
                download_path = improved_sketch.convert_to_pencil_sketch(original_path, add_watermark=True)
                
            print(f"Generated download sketch at: {download_path}")
            
            # Set a better filename for the download
            download_filename = f"Draw_AI_Sketch_{style}_{session_id[:8]}.jpg"
            
            # Return the file for download
            return send_file(
                download_path,
                as_attachment=True,
                download_name=download_filename,
                mimetype='image/jpeg'
            )
            
        except Exception as e:
            print(f"Error generating download sketch: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        print(f"Error during free sketch download: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
    Render a professional payment form for the local payment system
    """
    payment_id = request.args.get('payment_id')
    
    # Return HTML for an enhanced payment form that looks like a real payment processor
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Draw AI - Payment</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 0; 
                background-color: #f7f9fc; 
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            
            .payment-container {{ 
                max-width: 480px; 
                width: 100%;
                background: white; 
                padding: 30px; 
                border-radius: 12px; 
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); 
                margin: 20px;
            }}
            
            .logo-area {{
                text-align: center;
                margin-bottom: 25px;
            }}
            
            h1 {{ 
                font-size: 22px;
                color: #333; 
                text-align: center; 
                margin-bottom: 25px; 
                font-weight: 600;
            }}
            
            .form-group {{ 
                margin-bottom: 20px; 
            }}
            
            label {{ 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 500; 
                font-size: 14px;
                color: #555;
            }}
            
            input {{ 
                width: 100%; 
                padding: 12px; 
                border: 1px solid #ddd; 
                border-radius: 6px; 
                box-sizing: border-box; 
                font-size: 16px;
            }}
            
            button {{ 
                background-color: #4169e1; 
                color: white; 
                border: none;
                padding: 14px 20px; 
                border-radius: 6px;
                cursor: pointer; 
                width: 100%; 
                font-size: 16px;
                font-weight: 600;
            }}
            
            button:hover {{ 
                background-color: #3454c9;
            }}
            
            .input-row {{
                display: flex;
                gap: 15px;
            }}
            
            .input-row .form-group {{
                flex: 1;
            }}
            
            .amount-display {{
                text-align: center;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 30px;
                color: #333;
            }}
            
            .card-icons {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
                gap: 10px;
            }}
            
            .card-icon {{
                width: 40px;
                opacity: 0.7;
            }}
            
            .footer {{
                text-align: center;
                margin-top: 25px;
                font-size: 13px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="payment-container">
            <div class="logo-area">
                <h2 style="margin:0">Draw AI - Payment</h2>
            </div>
            
            <h1>Complete your purchase to remove the watermark</h1>
            
            <div class="amount-display">$1.00</div>
            
            <div class="card-icons">
                <img src="https://cdn-icons-png.flaticon.com/128/196/196578.png" alt="Visa" class="card-icon">
                <img src="https://cdn-icons-png.flaticon.com/128/196/196561.png" alt="Mastercard" class="card-icon">
                <img src="https://cdn-icons-png.flaticon.com/128/196/196539.png" alt="American Express" class="card-icon">
                <img src="https://cdn-icons-png.flaticon.com/128/196/196565.png" alt="Discover" class="card-icon">
            </div>
            
            <form id="payment-form" action="/payment/process" method="post">
                <input type="hidden" name="payment_id" value="{payment_id}">
                
                <div class="form-group">
                    <label for="card-number">Card Number</label>
                    <input type="text" id="card-number" name="card_number" placeholder="1234 5678 9012 3456" maxlength="19" required>
                </div>
                
                <div class="input-row">
                    <div class="form-group">
                        <label for="expiry">Expiration Date</label>
                        <input type="text" id="expiry" name="expiry" placeholder="MM/YY" maxlength="5" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="cvc">CVC</label>
                        <input type="text" id="cvc" name="cvc" placeholder="123" maxlength="4" required>
                    </div>
                </div>
                
                <button type="submit" id="submit-button">Pay Now</button>
                
                <div class="footer">
                    <p>Your payment information is secure</p>
                    <p style="font-size:11px; margin-top:5px">
                        Use any card number ending in 4242 to simulate a successful payment
                    </p>
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
    Process the payment form submission with realistic handling
    """
    payment_id = request.form.get('payment_id')
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvc = request.form.get('cvc')
    
    # Clean the input values
    if card_number:
        card_number = card_number.replace(' ', '')
    
    # Enhanced validation
    errors = {}
    if not payment_id:
        errors['payment_id'] = "Invalid payment session"
    if not card_number or len(card_number) < 13 or len(card_number) > 19:
        errors['card_number'] = "Please enter a valid card number"
    if not expiry or '/' not in expiry:
        errors['expiry'] = "Please enter a valid expiration date"
    if not cvc or len(cvc) < 3:
        errors['cvc'] = "Please enter a valid security code"
    
    if errors:
        return jsonify({"error": "Payment validation failed", "fields": errors}), 400
    
    # Add a short delay to simulate payment processing
    # This makes the experience more realistic
    time.sleep(1)
    
    # Process payment through our payment handler
    result = payments.process_payment(payment_id, card_number, expiry, cvc)
    
    if result['success']:
        # Show success with a professional confirmation page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Successful | Draw AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                :root {{
                    --success-color: #2ecc71;
                    --primary-color: #4169e1;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f7f9fc;
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                
                .success-container {{
                    max-width: 480px;
                    width: 100%;
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    text-align: center;
                    margin: 20px;
                }}
                
                .success-icon {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 25px;
                    background-color: var(--success-color);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .success-icon i {{
                    color: white;
                    font-size: 40px;
                }}
                
                h1 {{
                    font-size: 24px;
                    margin-bottom: 15px;
                    color: #333;
                }}
                
                p {{
                    color: #666;
                    margin-bottom: 25px;
                    font-size: 16px;
                }}
                
                .transaction-details {{
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 25px;
                    text-align: left;
                }}
                
                .transaction-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}
                
                .transaction-row:last-child {{
                    margin-bottom: 0;
                }}
                
                .transaction-row .label {{
                    color: #777;
                }}
                
                .transaction-row .value {{
                    font-weight: 600;
                    color: #333;
                }}
                
                .redirecting {{
                    margin-top: 30px;
                    font-size: 15px;
                    color: #888;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .spinner {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid rgba(0,0,0,0.1);
                    border-left-color: var(--primary-color);
                    border-radius: 50%;
                    margin-right: 10px;
                    animation: spin 1s linear infinite;
                }}
                
                @keyframes spin {{
                    to {{ transform: rotate(360deg); }}
                }}
            </style>
            <script>
                // Redirect after 3 seconds for a more professional experience
                setTimeout(function() {{
                    window.location.href = "{result['redirect_url']}";
                }}, 3000);
            </script>
        </head>
        <body>
            <div class="success-container">
                <div class="success-icon">
                    <i class="fas fa-check"></i>
                </div>
                
                <h1>Payment Successful!</h1>
                <p>Your payment has been processed successfully. You now have access to the premium version.</p>
                
                <div class="transaction-details">
                    <div class="transaction-row">
                        <span class="label">Amount:</span>
                        <span class="value">$1.00</span>
                    </div>
                    <div class="transaction-row">
                        <span class="label">Date:</span>
                        <span class="value">{datetime.now().strftime('%b %d, %Y')}</span>
                    </div>
                    <div class="transaction-row">
                        <span class="label">Payment Method:</span>
                        <span class="value">•••• {card_number[-4:]}</span>
                    </div>
                    <div class="transaction-row">
                        <span class="label">Transaction ID:</span>
                        <span class="value">{payment_id[:8].upper()}</span>
                    </div>
                </div>
                
                <div class="redirecting">
                    <div class="spinner"></div>
                    <span>Redirecting to your download...</span>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        # Show failure with clear explanation and retry option
        error_message = result.get('error', 'Transaction declined')
        error_code = result.get('code', 'unknown_error')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Failed | Draw AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                :root {{
                    --error-color: #e74c3c;
                    --primary-color: #4169e1;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f7f9fc;
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                
                .error-container {{
                    max-width: 480px;
                    width: 100%;
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    text-align: center;
                    margin: 20px;
                }}
                
                .error-icon {{
                    width: 80px;
                    height: 80px;
                    margin: 0 auto 25px;
                    background-color: var(--error-color);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .error-icon i {{
                    color: white;
                    font-size: 40px;
                }}
                
                h1 {{
                    font-size: 24px;
                    margin-bottom: 15px;
                    color: #333;
                }}
                
                p {{
                    color: #666;
                    margin-bottom: 25px;
                    font-size: 16px;
                }}
                
                .error-details {{
                    background-color: #fcf0ef;
                    border: 1px solid #fadbd8;
                    color: #a04034;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                    font-size: 15px;
                    text-align: left;
                }}
                
                .error-code {{
                    display: block;
                    font-size: 12px;
                    margin-top: 5px;
                    color: #e74c3c;
                    opacity: 0.7;
                }}
                
                .buttons {{
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                
                .button {{
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 15px;
                    text-decoration: none;
                    display: inline-block;
                    cursor: pointer;
                    transition: background-color 0.3s, transform 0.1s;
                }}
                
                .primary-button {{
                    background-color: var(--primary-color);
                    color: white;
                }}
                
                .primary-button:hover {{
                    background-color: #3454c9;
                }}
                
                .secondary-button {{
                    background-color: transparent;
                    color: #555;
                    border: 1px solid #ddd;
                }}
                
                .secondary-button:hover {{
                    background-color: #f5f5f5;
                }}
                
                .redirecting {{
                    margin-top: 30px;
                    font-size: 14px;
                    color: #888;
                }}
            </style>
            <script>
                // Redirect after 8 seconds to allow user to read the error
                setTimeout(function() {{
                    window.location.href = "{result['redirect_url']}";
                }}, 8000);
            </script>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">
                    <i class="fas fa-times"></i>
                </div>
                
                <h1>Payment Failed</h1>
                <p>We couldn't process your payment. Please check your payment details and try again.</p>
                
                <div class="error-details">
                    <strong>{error_message}</strong>
                    <span class="error-code">Error code: {error_code}</span>
                </div>
                
                <div class="buttons">
                    <a href="/payment/checkout?payment_id={payment_id}" class="button primary-button">
                        Try Again
                    </a>
                    <a href="{result['redirect_url']}" class="button secondary-button">
                        Go back to results
                    </a>
                </div>
                
                <div class="redirecting">
                    <p>Redirecting in 8 seconds...</p>
                </div>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
