# Deployment Plan: Render & Vercel

This document provides instructions for deploying the HDFC Mutual Fund FAQ Assistant.

## 1. Backend Deployment (Render)

The backend is a FastAPI application.

### Steps:
1.  **Connect GitHub**: Log in to [Render](https://render.com) and connect your GitHub repository.
2.  **Create Blueprint**: Click "New" -> "Blueprint". Render will automatically detect the `render.yaml` file.
3.  **Environment Variables**:
    *   `GROQ_API_KEY`: Your Groq API key.
    *   `PYTHON_VERSION`: `3.9.0` (set in `render.yaml`).
4.  **Deploy**: Render will build the service using `pip install -r requirements.txt` and start it with `gunicorn`.

**Backend URL**: Once deployed, Render will provide a URL like `https://hdfc-faq-backend.onrender.com`.

---

## 2. Frontend Deployment (Vercel)

The frontend is a Next.js application located in the `frontend/` directory.

### Steps:
1.  **Connect GitHub**: Log in to [Vercel](https://vercel.com) and import your repository.
2.  **Project Settings**:
    *   **Root Directory**: Set to `frontend`.
    *   **Framework Preset**: Next.js.
3.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: The URL of your Render backend (e.g., `https://hdfc-faq-backend.onrender.com`).
4.  **Deploy**: Vercel will build and deploy the application.

---

## 3. Post-Deployment Verification

1.  **Health Check**: Visit `https://your-backend-url.onrender.com/health`.
2.  **Metadata**: Visit `https://your-backend-url.onrender.com/meta` to ensure schemes are loaded.
3.  **Frontend**: Open your Vercel URL.
    *   Verify the sidebar displays the "Ingested Schemes".
    *   Ask a question (e.g., "What is the exit load for HDFC Mid Cap?") and verify the response and source citation.

## 4. Troubleshooting

*   **CORS Issues**: Ensure the backend's `CORSMiddleware` allows the Vercel frontend domain (currently set to `*` for convenience).
*   **API Timeouts**: Render's free tier may spin down after inactivity. The first request might take a few seconds to "wake up" the server.
