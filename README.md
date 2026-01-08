# Student Card Reader - Setup & Run Guide

This guide will help you run the Student Card Reader application on your local machine. The project consists of two parts: the **Backend** (Python/FastAPI) and the **Frontend** (React/Vite).

## Prerequisites
- Python 3.8+
- Node.js & npm
- Tesseract OCR (Optional, but recommended for better text extraction)

## 1. Starting the Backend
The backend handles image processing, database management, and the API.

1.  Open a terminal.
2.  Navigate to the project directory:
    ```bash
    cd /Users/ardayasan/CV-Student-Card-Reader
    ```
3.  Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4.  Run the backend server:
    ```bash
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
    ```
    *You should see "Application startup complete" and it will listen on http://localhost:8000.*

## 2. Starting the Frontend
The frontend is the web user interface.

1.  Open a **new** terminal window (keep the backend running).
2.  Navigate to the frontend directory:
    ```bash
    cd /Users/ardayasan/CV-Student-Card-Reader/frontend
    ```
3.  Run the development server:
    ```bash
    npm run dev -- --host
    ```
4.  Open your browser and go to:
    **http://localhost:5173**

## Common Issues
- **Port already in use**: If you see an error about port 8000 or 5173 being busy, make sure no other instances of the app are running. You can kill them with:
  ```bash
  lsof -t -i:8000 | xargs kill -9
  lsof -t -i:5173 | xargs kill -9
  ```
- **Dependencies**: If you get "module not found" errors, ensure you have installed dependencies:
  - Backend: `pip install -r requirements.txt` (if you haven't created one, you might need to install `fastapi uvicorn sqlalchemy opencv-python pytesseract python-dotenv numpy`)
  - Frontend: `npm install` inside the `frontend` directory.

## Stopping the App
To stop the application, simply press `Ctrl + C` in both terminal windows.
