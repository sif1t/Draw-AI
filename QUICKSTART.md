# Draw AI - Quick Start Guide

This guide will help you quickly set up and run the Draw AI application.

## Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Stripe account (for payment integration)

## Backend Setup

1. Open a terminal and navigate to the server directory:

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

5. Create a `.env` file based on `.env.example`:

```
# Windows PowerShell
Copy-Item .env.example .env

# Or manually create a .env file and add your Stripe API keys
```

6. Update the `.env` file with your Stripe API keys.

7. Run the Flask server:

```
python app.py
```

The backend should now be running at http://localhost:5000.

## Frontend Setup

1. Open a new terminal and navigate to the client directory:

```
cd client
```

2. Install dependencies:

```
npm install
```

3. Create a `.env` file based on `.env.development`:

```
# Windows PowerShell
Copy-Item .env.development .env.local
```

4. Start the React development server:

```
npm start
```

The frontend should now be running at http://localhost:3000.

## Testing the Application

1. Open your browser and go to http://localhost:3000
2. Upload an image using the interface
3. View the generated sketch with watermark
4. Test the payment flow (use Stripe test cards for testing)

## Stripe Test Cards

For testing the payment functionality, you can use these Stripe test cards:

- Success payment: 4242 4242 4242 4242
- Declined payment: 4000 0000 0000 0002

Use any future expiration date, any 3-digit CVC, and any postal code.

## Need Help?

If you encounter any issues, please refer to the full README.md file or reach out to the project maintainer.
