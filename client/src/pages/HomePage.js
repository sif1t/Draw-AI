import React from 'react';
import ImageUploader from '../components/ImageUploader';

const HomePage = () => {
    return (
        <div className="container mx-auto px-4 py-12">
            {/* Hero Section */}
            <section className="text-center mb-16">
                <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                    Turn Photos into Stunning Pencil Sketches
                </h1>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                    Transform your images into beautiful, hand-drawn style pencil sketches with our AI-powered tool.
                    Easy to use, instant results.
                </p>
                <div className="flex justify-center space-x-4">
                    <a href="#upload-section" className="btn btn-primary">
                        Try it Now
                    </a>
                    <a href="#" className="btn btn-outline">
                        Learn More
                    </a>
                </div>
            </section>

            {/* Upload Section */}
            <section id="upload-section" className="max-w-4xl mx-auto mb-20">
                <div className="card">
                    <h2 className="text-2xl font-bold text-center text-gray-800 mb-8">
                        Upload Your Image
                    </h2>
                    <ImageUploader />
                </div>
            </section>

            {/* Features Section */}
            <section className="mb-20">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
                    Why Choose Draw AI?
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="card text-center">
                        <div className="flex justify-center mb-4">
                            <svg
                                className="w-12 h-12 text-primary"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path fillRule="evenodd" d="M3 5a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm11 1H6v8l4-2 4 2V6z" clipRule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold mb-2">High Quality Sketches</h3>
                        <p className="text-gray-600">
                            Our advanced algorithm creates realistic pencil sketches that look hand-drawn.
                        </p>
                    </div>

                    <div className="card text-center">
                        <div className="flex justify-center mb-4">
                            <svg
                                className="w-12 h-12 text-primary"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Instant Results</h3>
                        <p className="text-gray-600">
                            Get your sketch in seconds. No waiting, no complicated process.
                        </p>
                    </div>

                    <div className="card text-center">
                        <div className="flex justify-center mb-4">
                            <svg
                                className="w-12 h-12 text-primary"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"></path>
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd"></path>
                            </svg>
                        </div>
                        <h3 className="text-xl font-semibold mb-2">Affordable Premium Option</h3>
                        <p className="text-gray-600">
                            Try for free with watermark, or get the premium version for just $1.
                        </p>
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section className="mb-20">
                <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
                    How It Works
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-2xl font-bold mb-4">
                            1
                        </div>
                        <h3 className="text-xl font-semibold mb-2 text-center">Upload Photo</h3>
                        <p className="text-gray-600 text-center">
                            Upload any JPG or PNG image that you want to convert.
                        </p>
                    </div>

                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-2xl font-bold mb-4">
                            2
                        </div>
                        <h3 className="text-xl font-semibold mb-2 text-center">AI Processing</h3>
                        <p className="text-gray-600 text-center">
                            Our AI algorithms transform your photo into a pencil sketch.
                        </p>
                    </div>

                    <div className="flex flex-col items-center">
                        <div className="w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-2xl font-bold mb-4">
                            3
                        </div>
                        <h3 className="text-xl font-semibold mb-2 text-center">Download Result</h3>
                        <p className="text-gray-600 text-center">
                            Download your sketch for free with watermark or pay for premium version.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default HomePage;
