import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const ImageUploader = () => {
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);
    const [sketchStyle, setSketchStyle] = useState('pencil'); // Default style
    const navigate = useNavigate();

    const onDrop = useCallback(async (acceptedFiles) => {
        // Reset error state
        setUploadError(null);

        // Validate file
        const file = acceptedFiles[0];
        if (!file) return;

        // Check file type
        if (!file.type.match(/image\/(jpeg|jpg|png)/i)) {
            setUploadError('Please upload a valid JPG or PNG image');
            return;
        }

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            setUploadError('Image size must be less than 5MB');
            return;
        }

        setIsUploading(true);

        try {
            console.log('Starting upload process');

            // Create form data
            const formData = new FormData();
            formData.append('image', file);
            formData.append('style', sketchStyle); // Add the selected style
            console.log('File added to form data:', file.name, file.type, file.size);
            console.log('Using sketch style:', sketchStyle);

            const apiUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/convert/style`;
            console.log('Sending request to:', apiUrl);

            // Send to backend with better error handling
            try {
                const response = await axios.post(
                    apiUrl,
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        },
                        // Increase timeout for large images
                        timeout: 30000
                    }
                );

                console.log('Response received:', response.data);

                if (response.data.success) {
                    // Navigate to result page with sketch data
                    navigate('/result', {
                        state: {
                            sketch: response.data.sketch,
                            sessionId: response.data.session_id,
                            originalImage: URL.createObjectURL(file),
                            style: response.data.style || sketchStyle
                        }
                    });
                } else {
                    console.error('API returned success=false:', response.data);
                    setUploadError(`Failed to convert image: ${response.data.error || 'Unknown error'}`);
                }
            } catch (axiosError) {
                console.error('Axios error details:', axiosError);

                if (axiosError.response) {
                    // Server responded with non-2xx status code
                    console.error('Error response:', axiosError.response.data);
                    setUploadError(`Server error: ${axiosError.response.data.error || axiosError.response.status}`);
                } else if (axiosError.request) {
                    // Request was made but no response received
                    console.error('No response received');
                    setUploadError('Server not responding. Please check your connection.');
                } else {
                    // Error setting up the request
                    console.error('Request setup error');
                    setUploadError(`Request error: ${axiosError.message}`);
                }
            }
        } catch (error) {
            console.error('General error:', error);
            setUploadError(`An error occurred: ${error.message}`);
        } finally {
            setIsUploading(false);
        }
    }, [navigate, sketchStyle]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

    return (
        <div className="w-full max-w-lg mx-auto">
            {/* Style Selection */}
            <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-700 mb-2">Choose Sketch Style</h3>
                <div className="flex flex-wrap gap-3 justify-center">
                    <button
                        className={`px-4 py-2 rounded-md ${sketchStyle === 'pencil' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setSketchStyle('pencil')}
                    >
                        Pencil Sketch
                    </button>
                    <button
                        className={`px-4 py-2 rounded-md ${sketchStyle === 'realistic' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setSketchStyle('realistic')}
                    >
                        Realistic Sketch
                    </button>
                    <button
                        className={`px-4 py-2 rounded-md ${sketchStyle === 'portrait' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setSketchStyle('portrait')}
                    >
                        Artistic Portrait
                    </button>
                    <button
                        className={`px-4 py-2 rounded-md ${sketchStyle === 'ultra-clear' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setSketchStyle('ultra-clear')}
                    >
                        Authentic Pencil
                    </button>
                </div>
                <div className="mt-2 text-center text-xs text-gray-500">
                    Authentic Pencil creates truly realistic hand-drawn sketch effects
                </div>
            </div>

            <div
                {...getRootProps()}
                className={`drop-zone ${isDragActive ? 'active' : ''}`}
            >
                <input {...getInputProps()} />

                <svg
                    className="w-16 h-16 text-gray-400 mb-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1.5"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                </svg>

                {isUploading ? (
                    <p className="text-gray-600 text-center">Uploading...</p>
                ) : (
                    <>
                        <p className="text-lg font-medium text-gray-700 mb-1">
                            {isDragActive ? 'Drop your image here' : 'Drag & drop your image here'}
                        </p>
                        <p className="text-sm text-gray-500 mb-4">or click to browse files</p>
                        <p className="text-xs text-gray-400">
                            Supported formats: JPG, PNG (max 5MB)
                        </p>
                    </>
                )}
            </div>

            {uploadError && (
                <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-md text-center">
                    {uploadError}
                </div>
            )}

            <div className="mt-6 text-center">
                <button
                    className="btn btn-primary"
                    disabled={isUploading}
                    onClick={() => document.querySelector('input[type="file"]').click()}
                >
                    {isUploading ? 'Converting...' : 'Upload & Convert'}
                </button>
            </div>
        </div>
    );
};

export default ImageUploader;
