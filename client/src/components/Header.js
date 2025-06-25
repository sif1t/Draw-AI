import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
    return (
        <header className="bg-white shadow-sm">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                <Link to="/" className="flex items-center">
                    <svg
                        className="w-8 h-8 mr-2 text-primary"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                    </svg>
                    <span className="text-xl font-bold text-gray-900">Draw AI</span>
                </Link>
                <nav>
                    <ul className="flex space-x-6">
                        <li>
                            <Link to="/" className="text-gray-600 hover:text-primary font-medium">
                                Home
                            </Link>
                        </li>
                        <li>
                            <Link to="/about" className="text-gray-600 hover:text-primary font-medium">
                                About
                            </Link>
                        </li>
                        <li>
                            <Link to="/contact" className="text-gray-600 hover:text-primary font-medium">
                                Contact
                            </Link>
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    );
};

export default Header;
