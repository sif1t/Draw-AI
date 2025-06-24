import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(price_id, success_url, cancel_url):
    """
    Create a Stripe checkout session
    
    Args:
        price_id: Stripe price ID
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
    
    Returns:
        Checkout session ID and URL
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return {
            'id': checkout_session.id,
            'url': checkout_session.url
        }
    except Exception as e:
        return {'error': str(e)}

def verify_payment_intent(payment_intent_id):
    """
    Verify a payment intent
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        Boolean indicating if the payment was successful
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent.status == 'succeeded'
    except Exception as e:
        return False
