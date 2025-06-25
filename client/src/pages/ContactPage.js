import React, { useState } from 'react';

const ContactPage = () => {
    const [formState, setFormState] = useState({
        name: '',
        email: '',
        subject: '',
        message: '',
    });

    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormState((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Simple validation
        if (!formState.name || !formState.email || !formState.message) {
            setError(true);
            return;
        }

        // In a real application, you would send the form data to a backend API
        // For now, we'll just simulate a successful submission
        setTimeout(() => {
            setSubmitted(true);
            setError(false);
            // Reset form
            setFormState({
                name: '',
                email: '',
                subject: '',
                message: '',
            });
        }, 1000);
    };

    return (
        <div className="container mx-auto px-4 py-12">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Contact Us</h1>

                <div className="grid md:grid-cols-2 gap-10">
                    {/* Contact Information */}
                    <div>
                        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
                            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Get In Touch</h2>
                            <p className="text-gray-600 mb-6">
                                Have questions about Draw AI? Looking for support or business inquiries?
                                We'd love to hear from you! Fill out the form or use our contact details below.
                            </p>

                            <div className="space-y-4">
                                <div className="flex items-start">
                                    <svg className="w-6 h-6 text-primary mt-1 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"></path>
                                    </svg>
                                    <div>
                                        <h3 className="font-medium text-gray-800">Address</h3>
                                        <p className="text-gray-600">
                                            123 AI Boulevard<br />
                                            Tech District<br />
                                            Innovation City, IC 10101
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-start">
                                    <svg className="w-6 h-6 text-primary mt-1 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"></path>
                                    </svg>
                                    <div>
                                        <h3 className="font-medium text-gray-800">Phone</h3>
                                        <p className="text-gray-600">+1 (555) 123-4567</p>
                                    </div>
                                </div>

                                <div className="flex items-start">
                                    <svg className="w-6 h-6 text-primary mt-1 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                                        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                                    </svg>
                                    <div>
                                        <h3 className="font-medium text-gray-800">Email</h3>
                                        <p className="text-gray-600">contact@drawai.com</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-md p-8">
                            <h2 className="text-2xl font-semibold mb-4 text-gray-700">Business Hours</h2>
                            <ul className="space-y-2 text-gray-600">
                                <li className="flex justify-between">
                                    <span>Monday - Friday:</span>
                                    <span>9:00 AM - 6:00 PM</span>
                                </li>
                                <li className="flex justify-between">
                                    <span>Saturday:</span>
                                    <span>10:00 AM - 4:00 PM</span>
                                </li>
                                <li className="flex justify-between">
                                    <span>Sunday:</span>
                                    <span>Closed</span>
                                </li>
                            </ul>
                        </div>
                    </div>

                    {/* Contact Form */}
                    <div className="bg-white rounded-lg shadow-md p-8">
                        <h2 className="text-2xl font-semibold mb-6 text-gray-700">Send Us a Message</h2>

                        {submitted ? (
                            <div className="bg-green-50 border-l-4 border-green-500 p-5 rounded mb-6">
                                <div className="flex">
                                    <div className="flex-shrink-0">
                                        <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                                        </svg>
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm text-green-700">
                                            Thank you for your message! We'll get back to you as soon as possible.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleSubmit}>
                                {error && (
                                    <div className="bg-red-50 border-l-4 border-red-500 p-5 rounded mb-6">
                                        <div className="flex">
                                            <div className="flex-shrink-0">
                                                <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
                                                </svg>
                                            </div>
                                            <div className="ml-3">
                                                <p className="text-sm text-red-700">
                                                    Please fill in all required fields.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="mb-4">
                                    <label htmlFor="name" className="block text-gray-700 font-medium mb-2">
                                        Your Name <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="text"
                                        id="name"
                                        name="name"
                                        value={formState.name}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-primary"
                                        required
                                    />
                                </div>

                                <div className="mb-4">
                                    <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
                                        Email Address <span className="text-red-500">*</span>
                                    </label>
                                    <input
                                        type="email"
                                        id="email"
                                        name="email"
                                        value={formState.email}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-primary"
                                        required
                                    />
                                </div>

                                <div className="mb-4">
                                    <label htmlFor="subject" className="block text-gray-700 font-medium mb-2">
                                        Subject
                                    </label>
                                    <input
                                        type="text"
                                        id="subject"
                                        name="subject"
                                        value={formState.subject}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-primary"
                                    />
                                </div>

                                <div className="mb-6">
                                    <label htmlFor="message" className="block text-gray-700 font-medium mb-2">
                                        Message <span className="text-red-500">*</span>
                                    </label>
                                    <textarea
                                        id="message"
                                        name="message"
                                        value={formState.message}
                                        onChange={handleChange}
                                        rows="5"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-primary"
                                        required
                                    ></textarea>
                                </div>

                                <button
                                    type="submit"
                                    className="bg-primary text-white py-3 px-6 rounded-md hover:bg-primary-dark transition duration-300 w-full font-medium"
                                >
                                    Send Message
                                </button>
                            </form>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ContactPage;
