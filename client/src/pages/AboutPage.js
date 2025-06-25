import React from 'react';

const AboutPage = () => {
    return (
        <div className="container mx-auto px-4 py-12">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">About Draw AI</h1>

                <div className="bg-white rounded-lg shadow-md p-8 mb-10">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-700">Our Story</h2>
                    <p className="text-gray-600 mb-6 leading-relaxed">
                        Draw AI was founded in 2025 with a simple but powerful vision: to make artistic transformation
                        accessible to everyone. Our team of developers and AI enthusiasts came together to create a
                        tool that bridges the gap between photography and traditional artistic mediums.
                    </p>
                    <p className="text-gray-600 mb-6 leading-relaxed">
                        What started as a passion project quickly evolved into a powerful platform that uses
                        advanced neural networks to transform ordinary photos into stunning pencil sketches that
                        capture the essence and emotion of the original images.
                    </p>
                </div>

                <div className="bg-white rounded-lg shadow-md p-8 mb-10">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-700">Our Technology</h2>
                    <p className="text-gray-600 mb-6 leading-relaxed">
                        Draw AI uses a sophisticated computer vision algorithm that analyzes the details, edges,
                        and contours of your images to create realistic pencil sketches. Our technology doesn't
                        simply apply a filter—it reinterprets your image with the precision and style of a
                        traditional artist.
                    </p>
                    <div className="bg-gray-50 border-l-4 border-primary p-5 rounded">
                        <h3 className="font-semibold text-lg mb-2">Key Features:</h3>
                        <ul className="list-disc pl-5 space-y-2 text-gray-600">
                            <li>Advanced edge detection for realistic sketch lines</li>
                            <li>Smart shading to preserve depth and dimension</li>
                            <li>Texture analysis that mimics traditional sketching techniques</li>
                            <li>High-resolution output for perfect prints</li>
                        </ul>
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-md p-8">
                    <h2 className="text-2xl font-semibold mb-4 text-gray-700">Why Choose Draw AI?</h2>
                    <div className="grid md:grid-cols-2 gap-6 mb-6">
                        <div className="border border-gray-200 rounded-lg p-5">
                            <div className="flex items-center mb-3">
                                <svg className="w-6 h-6 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                </svg>
                                <h3 className="font-semibold">User-Friendly</h3>
                            </div>
                            <p className="text-gray-600">
                                Simple interface that makes artistic transformation accessible to everyone,
                                regardless of technical skill.
                            </p>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-5">
                            <div className="flex items-center mb-3">
                                <svg className="w-6 h-6 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                </svg>
                                <h3 className="font-semibold">High Quality</h3>
                            </div>
                            <p className="text-gray-600">
                                Professional-grade sketch conversion that preserves the details and emotions of
                                your original photos.
                            </p>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-5">
                            <div className="flex items-center mb-3">
                                <svg className="w-6 h-6 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                </svg>
                                <h3 className="font-semibold">Fast Processing</h3>
                            </div>
                            <p className="text-gray-600">
                                Quick conversion process that delivers your sketch within seconds, not minutes.
                            </p>
                        </div>

                        <div className="border border-gray-200 rounded-lg p-5">
                            <div className="flex items-center mb-3">
                                <svg className="w-6 h-6 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                </svg>
                                <h3 className="font-semibold">Premium Options</h3>
                            </div>
                            <p className="text-gray-600">
                                Affordable premium upgrade for watermark-free downloads and commercial usage rights.
                            </p>
                        </div>
                    </div>
                    <p className="text-center text-gray-600 italic mt-6">
                        "Our mission is to make artistic expression accessible to everyone through technology."
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AboutPage;
