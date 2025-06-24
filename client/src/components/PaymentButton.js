import React, { useState } from 'react';
import axios from 'axios';

const PaymentButton = ({ sessionId, onPaymentSuccess }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handlePayment = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Create Stripe checkout session
            const response = await axios.post(
                `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/create-checkout-session`,
                { session_id: sessionId }
            );

            if (response.data.url) {
                // Redirect to Stripe Checkout
                window.location.href = response.data.url;
            } else {
                throw new Error('Failed to create checkout session');
            }
        } catch (error) {
            console.error('Payment error:', error);
            setError('Failed to initialize payment. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <button
                className="btn btn-secondary w-full md:w-auto"
                onClick={handlePayment}
                disabled={isLoading}
            >
                {isLoading ? 'Processing...' : 'Remove Watermark - $1'}
            </button>

            {error && (
                <div className="mt-2 text-sm text-red-600">
                    {error}
                </div>
            )}
        </div>
    );
};

export default PaymentButton;
