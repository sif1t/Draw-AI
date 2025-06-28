# Draw AI - Professional Pencil Sketch Generator

Draw AI is a full-featured web application that allows users to upload an image and convert it into professional-quality pencil sketches using advanced image processing. The app includes free sketch creation with multiple artistic styles and a premium download option (without watermark) through an integrated payment system.

## Features

- **Multiple Professional Sketch Styles**:
  - **Basic Pencil Sketch**: Clean, high-contrast pencil sketch style
  - **Realistic Pencil Sketch**: Natural-looking sketch with smooth shading
  - **Artistic Portrait**: Professional artist-quality sketch similar to hand-drawn portraits
  - **Authentic Pencil**: Professional hand-drawn pencil portrait with deep blacks, fine details, and realistic shading that closely mimics artwork done by professional portrait artists
- Image Upload (JPG/PNG)
- AI-powered Advanced Sketch Generator
- Preview Output with Watermark
- Premium Purchase Option ($1)
- Stripe Payment Integration
- Mobile Responsive Design
- Standalone Command-Line Tool

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

## Standalone Tool Usage

For those who prefer using a command-line interface, the standalone sketch tool is available:

```
python standalone_sketch.py [image_path] [-o output_path] [-m mode]
```

Options:
- `image_path`: Path to the input image (required)
- `-o, --output`: Path to save the output image (optional)
- `-m, --mode`: Sketch mode - 'regular', 'realistic', or 'artistic' (default: 'artistic')

Example:
```
python standalone_sketch.py my_photo.jpg -o my_sketch.jpg -m artistic
```

## Testing Tool

To compare all available sketch styles on a single image:

```
python server/test_all_sketch_styles.py [image_path] [-o output_directory]
```

This will generate all three types of sketches and save them in the specified directory.
