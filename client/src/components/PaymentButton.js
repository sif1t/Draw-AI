import React, { useState } from 'react';
import axios from 'axios';

const PaymentButton = ({ sessionId, onPaymentSuccess }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null); const handlePayment = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log('Initiating payment for session:', sessionId);

            // Create checkout session with our local payment system
            const response = await axios.post(
                `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/create-checkout-session`,
                { session_id: sessionId }
            );

            console.log('Checkout session response:', response.data);

            if (response.data.url) {
                // Redirect to local payment page
                window.location.href = `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${response.data.url}`;
            } else if (response.data.error) {
                throw new Error(response.data.error);
            } else {
                throw new Error('Failed to create checkout session');
            }
        } catch (error) {
            console.error('Payment error:', error);

            // Extract useful error information from various possible error formats
            let errorMessage;
            if (error.response?.data?.error) {
                errorMessage = error.response.data.error;
            } else if (error.message && error.message.includes('API Key')) {
                errorMessage = 'Payment system configuration error. Please contact support.';
            } else {
                errorMessage = error.message || 'Failed to initialize payment. Please try again.';
            }

            setError(errorMessage);
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
