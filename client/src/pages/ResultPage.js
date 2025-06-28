import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import PaymentButton from '../components/PaymentButton';

const ResultPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [originalImage, setOriginalImage] = useState(null);
    const [sketchImage, setSketchImage] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const [premiumSketch, setPremiumSketch] = useState(null);
    const [paymentSuccess, setPaymentSuccess] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState(null);    // Parse URL parameters for payment success
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const paymentStatus = params.get('payment_status');
        const sessionIdParam = params.get('session_id');

        if (paymentStatus === 'success' && sessionIdParam) {
            setPaymentSuccess(true);
            setSessionId(sessionIdParam);

            // Fetch the premium sketch
            const fetchPremiumSketch = async () => {
                try {
                    console.log("Fetching premium sketch for session:", sessionIdParam);
                    const response = await fetch(
                        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/get-premium-sketch?session_id=${sessionIdParam}`
                    );

                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    console.log("Premium sketch response:", data);

                    if (data.success) {
                        setPremiumSketch(`data:image/jpeg;base64,${data.premium_sketch}`);
                        setDownloadUrl(data.download_url);
                    } else {
                        console.error('Failed to get premium sketch:', data.error);
                    }
                } catch (error) {
                    console.error('Failed to fetch premium sketch:', error);
                }
            };

            fetchPremiumSketch();
        }
    }, []);

    // Get data from location state
    useEffect(() => {
        if (location.state) {
            const { sketch, sessionId: id, originalImage: origImg } = location.state;

            if (sketch && id) {
                setSketchImage(`data:image/jpeg;base64,${sketch}`);
                setSessionId(id);

                if (origImg) {
                    setOriginalImage(origImg);
                }
            } else {
                // Redirect to home if no data
                navigate('/');
            }
        } else if (!paymentSuccess) {
            // Redirect to home if no state and not coming from payment
            navigate('/');
        }
    }, [location, navigate, paymentSuccess]); const handleDownload = (imageUrl, isPremium) => {
        if (isPremium) {
            // Download from data URL for premium sketch during preview
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = 'premium_sketch.jpg';
            link.click();
        } else {
            // Use the API endpoint to ensure watermark is applied
            window.location.href = `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/download/free/${sessionId}`;
        }
    };

    if (!sketchImage && !premiumSketch) {
        return (
            <div className="container mx-auto px-4 py-12 text-center">
                <div className="card max-w-lg mx-auto">
                    <h2 className="text-2xl font-bold mb-4">Loading...</h2>
                    <p>Please wait while we process your image.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-12">
            <div className="max-w-5xl mx-auto">
                {paymentSuccess ? (
                    // Payment Success View
                    <div className="card mb-8">
                        <div className="text-center mb-6">
                            <svg
                                className="w-16 h-16 text-green-500 mx-auto mb-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                            </svg>
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">
                                Payment Successful!
                            </h2>
                            <p className="text-gray-600 mb-4">
                                Thank you for your purchase. Your premium sketch is ready to download.
                            </p>
                        </div>

                        <div className="mb-6">
                            <div className="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden mb-4">
                                <img
                                    src={premiumSketch}
                                    alt="Premium Sketch"
                                    className="w-full h-auto object-contain"
                                />
                            </div>
                            <div className="text-center">
                                <button
                                    className="btn btn-primary"
                                    onClick={() => {
                                        if (downloadUrl) {
                                            window.location.href = `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}${downloadUrl}`;
                                        } else {
                                            handleDownload(premiumSketch, true);
                                        }
                                    }}
                                >
                                    Download Premium Sketch
                                </button>
                            </div>
                        </div>

                        <div className="text-center">
                            <button
                                className="text-primary hover:underline"
                                onClick={() => navigate('/')}
                            >
                                Convert Another Image
                            </button>
                        </div>
                    </div>
                ) : (
                    // Normal Result View
                    <>
                        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">
                            Your Sketch Result
                        </h1>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                            {originalImage && (
                                <div className="card">
                                    <h3 className="text-xl font-semibold mb-4">Original Image</h3>
                                    <div className="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden">
                                        <img
                                            src={originalImage}
                                            alt="Original"
                                            className="w-full h-auto object-contain"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="card">
                                <h3 className="text-xl font-semibold mb-4">Pencil Sketch (Free Version)</h3>
                                <div className="aspect-w-16 aspect-h-9 rounded-lg overflow-hidden mb-4">
                                    <img
                                        src={sketchImage}
                                        alt="Sketch"
                                        className="w-full h-auto object-contain"
                                    />
                                </div>
                                <p className="text-sm text-gray-500 mb-4 text-center">
                                    This free version includes the "Draw AI" watermark
                                </p>
                                <div className="flex flex-col md:flex-row justify-center gap-4">
                                    <button
                                        className="btn btn-outline"
                                        onClick={() => handleDownload(sketchImage, false)}
                                    >
                                        Download Free Version
                                    </button>
                                    <PaymentButton
                                        sessionId={sessionId}
                                        onPaymentSuccess={() => { }}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <h2 className="text-xl font-semibold mb-4">Premium Upgrade Benefits</h2>
                            <ul className="space-y-2 mb-6">
                                <li className="flex items-start">
                                    <svg
                                        className="w-5 h-5 text-green-500 mr-2 mt-0.5"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                    </svg>
                                    <span>High-resolution output</span>
                                </li>
                                <li className="flex items-start">
                                    <svg
                                        className="w-5 h-5 text-green-500 mr-2 mt-0.5"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                    </svg>
                                    <span>No watermark</span>
                                </li>
                                <li className="flex items-start">
                                    <svg
                                        className="w-5 h-5 text-green-500 mr-2 mt-0.5"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                        xmlns="http://www.w3.org/2000/svg"
                                    >
                                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                    </svg>
                                    <span>Commercial usage rights</span>
                                </li>
                            </ul>
                            <div className="text-center">
                                <PaymentButton
                                    sessionId={sessionId}
                                    onPaymentSuccess={() => { }}
                                />
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ResultPage;
