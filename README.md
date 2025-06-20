# ContentGen

ContentGen is a simple SaaS example that uses OpenAI's GPT models to generate marketing content. It features a FastAPI backend and a React + Tailwind CSS frontend built with Vite.

## Requirements
- Python 3.10+
- Node.js 16+
- An OpenAI API key

## Backend
The backend lives in the `backend/` folder and exposes several endpoints for generating content. To run it locally:

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_key
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Frontend
The frontend lives in the `frontend/` folder and was bootstrapped with Vite. To start it:

```bash
cd frontend
npm install
npm run dev
```

The app will open on `http://localhost:3000` and will communicate with the backend running on port 8000.

## Features
- Generate product descriptions
- Generate blog posts
- Suggest hashtags
- Translate text

Free users are limited to five generations per day via a simple in-memory rate limiter.
