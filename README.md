# HDFC Mutual Fund FAQ Assistant

A trustworthy, transparent, and compliant mutual fund FAQ assistant that prioritizes accuracy over intelligence. Built for the NextLeap AI Challenge.

## 🛡️ Disclaimer
**“Facts-only. No investment advice.”**

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Groq API Key (for Llama-3.3-70b reasoning)

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chatbot_new
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Initialize Data:**
   Run the ingestion pipeline to fetch and index the latest HDFC data:
   ```bash
   python -m src.mf_faq.ingestion.refresh
   ```

5. **Run the Application:**
   
   **Backend (FastAPI):**
   ```bash
   python -m src.mf_faq.ui.backend
   ```
   
   **Frontend (Next.js):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🌐 Deployment
This project is designed to be deployed as a decoupled system:
- **Backend**: Deployed on [Render](https://render.com) (see `render.yaml`).
- **Frontend**: Deployed on [Vercel](https://vercel.com) (root directory: `frontend`).

Detailed instructions can be found in [deployment_plan.md](file:///c:/Users/Karuna/OneDrive/Desktop/nextleap/chatbot_new/docs/deployment_plan.md).

## 📈 Selected AMC & Schemes
**AMC:** HDFC Mutual Fund
**Schemes:**
1. HDFC Mid-Cap Opportunities Fund
2. HDFC Flexi Cap Fund (Equity Fund)
3. HDFC Focused 30 Fund
4. HDFC ELSS Tax Saver Fund
5. HDFC Top 100 Fund (Large Cap)

## 🏗️ Architecture Overview (RAG Approach)
The system uses a **Retrieval-Augmented Generation (RAG)** pipeline optimized for financial accuracy:
1. **Ingestion**: Asynchronous scraping of official `groww.in` product pages for HDFC schemes.
2. **Indexing**: Hybrid BM25 Sparse Indexer to handle specific financial terminology without the "hallucination" risks of dense vectors.
3. **Retrieval**: Unified retriever with:
   - Alias resolution (e.g., "Focused 30" -> Focused Fund).
   - Atomic chunk boosting (1.5x) for key statistics (NAV, Expense Ratio).
4. **Reasoning**: Groq-powered Llama-3.3-70b engine with a strict "Facts-Only" system prompt.
5. **Refusal Handling**: Automatic detection of advisory or performance-related queries, redirecting users to AMFI educational resources or official factsheets.

## ⚠️ Known Limitations
- **Data Freshness**: Relies on the daily ingestion trigger (configured via GitHub Actions).
- **Scope**: Limited to the 5 selected HDFC schemes.
- **Deep Comparisons**: Complex multi-fund comparisons are limited by the context window and BM25 ranking depth.

## 🤝 Compliance & Security
- **No PII**: All responses are scrubbed of PAN, Aadhaar, and contact details via regex.
- **Strict Refusals**: Any advisory query ("Should I invest?") is blocked and met with an educational disclaimer.
- **Source-Backed**: Every answer includes a direct link to the official product page and the "Last Updated" date.
