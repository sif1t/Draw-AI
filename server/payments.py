import os
import uuid
import json
import time
import random
import string
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Simple in-memory payment database
# In a real application, this would be a database
PAYMENTS = {}

def detect_card_type(card_number):
    """
    Detect the card type based on its number
    
    Args:
        card_number: Credit card number
    
    Returns:
        String representing the card type
    """
    if not card_number:
        return "Unknown"
        
    # Clean the number
    clean_number = card_number.replace(' ', '')
    
    # Check the first digits to determine card network
    if clean_number.startswith('4'):
        return "Visa"
    elif (clean_number.startswith('51') or 
          clean_number.startswith('52') or 
          clean_number.startswith('53') or 
          clean_number.startswith('54') or 
          clean_number.startswith('55') or
          (int(clean_number[:2]) >= 22 and int(clean_number[:2]) <= 27)):
        return "MasterCard"
    elif clean_number.startswith('34') or clean_number.startswith('37'):
        return "American Express"
    elif clean_number.startswith('6'):
        return "Discover"
    else:
        return "Credit Card"

def generate_transaction_id():
    """
    Generate a realistic-looking transaction ID
    
    Returns:
        A string representing a transaction ID
    """
    # Format: 2 letters + 6 numbers + 2 letters
    # Example: TX123456AB
    letters = string.ascii_uppercase
    prefix = ''.join(random.choices(letters, k=2))
    numbers = ''.join(random.choices(string.digits, k=6))
    suffix = ''.join(random.choices(letters, k=2))
    
    return f"{prefix}{numbers}{suffix}"

def create_checkout_session(price_id, success_url, cancel_url):
    """
    Create a local checkout session
    
    Args:
        price_id: Price ID (not used in local system)
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
    
    Returns:
        Checkout session ID and URL
    """
    try:
        # Create a unique payment ID
        payment_id = str(uuid.uuid4())
        
        # Store payment details
        PAYMENTS[payment_id] = {
            'created': datetime.now().isoformat(),
            'amount': 1.00,  # $1.00 fixed price
            'status': 'pending',
            'success_url': success_url,
            'cancel_url': cancel_url
        }
        
        # Instead of Stripe URL, create a local payment page URL
        checkout_url = f"/payment/checkout?payment_id={payment_id}"
        
        return {
            'id': payment_id,
            'url': checkout_url
        }
    except Exception as e:
        print(f"Error creating checkout: {str(e)}")
        return {'error': str(e)}

def verify_payment_intent(payment_id):
    """
    Verify a payment
    
    Args:
        payment_id: Local payment ID
    
    Returns:
        Boolean indicating if the payment was successful
    """
    try:
        if payment_id in PAYMENTS:
            return PAYMENTS[payment_id]['status'] == 'succeeded'
        return False
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        return False

def process_payment(payment_id, card_number, expiry_date, cvc):
    """
    Process a payment with the provided card details with realistic handling
    
    Args:
        payment_id: Local payment ID
        card_number: Credit card number
        expiry_date: Card expiry date (MM/YY)
        cvc: Card verification code
    
    Returns:
        Dict with success flag, possible error, and redirect URL
    """
    try:
        if payment_id not in PAYMENTS:
            return {
                'success': False, 
                'error': 'Invalid payment session', 
                'code': 'session_expired',
                'redirect_url': '/'
            }
        
        # Store last 4 digits of the card and card type for receipt
        PAYMENTS[payment_id]['card_last4'] = card_number[-4:]
        PAYMENTS[payment_id]['payment_method'] = detect_card_type(card_number)
        
        # Simulate different payment responses based on card number
        # This makes testing more realistic by simulating different payment scenarios
        
        # Success case - any card ending in 4242 (like Stripe test cards)
        if card_number.endswith('4242'):
            # Mark payment as succeeded
            PAYMENTS[payment_id]['status'] = 'succeeded'
            PAYMENTS[payment_id]['processed'] = datetime.now().isoformat()
            PAYMENTS[payment_id]['transaction_id'] = generate_transaction_id()
            
            return {
                'success': True,
                'redirect_url': PAYMENTS[payment_id]['success_url'],
                'transaction_id': PAYMENTS[payment_id]['transaction_id']
            }
        
        # Different error cases - to simulate real payment gateway errors
        elif card_number.endswith('0000'):
            return {
                'success': False,
                'error': 'Your card has insufficient funds.',
                'code': 'card_declined_insufficient_funds',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
        elif card_number.endswith('0001'):
            return {
                'success': False,
                'error': 'Your card has expired.',
                'code': 'card_expired',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
        elif card_number.endswith('0002'):
            return {
                'success': False,
                'error': 'Your card was declined by the issuer.',
                'code': 'card_declined_by_issuer',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
        elif card_number.endswith('0003'):
            return {
                'success': False,
                'error': 'The security code (CVC) is incorrect.',
                'code': 'incorrect_cvc',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
        # Default declined case
        else:
            return {
                'success': False,
                'error': 'Your card was declined. Please use a different payment method.',
                'code': 'card_declined',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return {'success': False, 'error': str(e)}
