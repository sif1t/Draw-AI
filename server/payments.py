import os
import uuid
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Simple in-memory payment database
# In a real application, this would be a database
PAYMENTS = {}

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
    Process a payment with the provided card details
    
    Args:
        payment_id: Local payment ID
        card_number: Credit card number
        expiry_date: Card expiry date (MM/YY)
        cvc: Card verification code
    
    Returns:
        Dict with success flag and redirect URL
    """
    try:
        if payment_id not in PAYMENTS:
            return {'success': False, 'error': 'Invalid payment ID'}
        
        # Simulate payment validation
        # Accept any card number ending in 4242 (like Stripe test cards)
        if card_number.endswith('4242'):
            # Mark payment as succeeded
            PAYMENTS[payment_id]['status'] = 'succeeded'
            PAYMENTS[payment_id]['processed'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'redirect_url': PAYMENTS[payment_id]['success_url']
            }
        else:
            return {
                'success': False,
                'error': 'Card declined',
                'redirect_url': PAYMENTS[payment_id]['cancel_url']
            }
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return {'success': False, 'error': str(e)}
