/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    light: '#4da8ff',
                    DEFAULT: '#1a86ff',
                    dark: '#0066cc',
                },
                secondary: {
                    light: '#ff7e5f',
                    DEFAULT: '#ff5e3a',
                    dark: '#e5492a',
                },
            },
            fontFamily: {
                sans: ['Poppins', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
