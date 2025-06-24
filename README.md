# Draw AI

Draw AI is a full-featured web application that allows users to upload an image and convert it into a realistic pencil sketch using Python-based image processing. The app includes a free sketch preview (with watermark) and a premium download option (without watermark) through an integrated payment system.

## Features

- Image Upload (JPG/PNG)
- AI-powered Sketch Generator
- Preview Output with Watermark
- Premium Purchase Option ($1)
- Stripe Payment Integration
- Mobile Responsive Design

## Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Axios
- React Router

### Backend
- Python (Flask)
- OpenCV / Pillow (image processing)
- Stripe API (payment gateway)

## Project Structure

```
draw-ai/
├── client/      (React App)
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.js
│   │   └── index.js
│   ├── .env.development
│   └── package.json
├── server/      (Python Backend)
│   ├── app.py (API)
│   ├── sketch.py (Image Processing)
│   ├── payments.py (Stripe)
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the server directory:
   ```
   cd server
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file based on `.env.example` and add your Stripe API keys.

6. Run the Flask server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the client directory:
   ```
   cd client
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file based on `.env.development` and update API URLs if needed.

4. Start the React development server:
   ```
   npm start
   ```

## Deployment

### Frontend
- The React app can be deployed on Vercel or Netlify.

### Backend
- The Flask server can be deployed on Render, Railway, or Heroku.

## Payment System

The app uses Stripe for payment processing. When a user clicks "Remove Watermark", they are redirected to a Stripe checkout page where they can pay $1 to download the premium version of the sketch (without watermark).

## Future Enhancements

- Additional sketch styles and filters
- User accounts and saved sketches history
- Bulk processing of multiple images
- Email delivery of sketches
- Admin dashboard for analytics
