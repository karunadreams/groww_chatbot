# Mutual Fund FAQ Assistant: Phase-wise Architecture

This document outlines the high-fidelity architectural roadmap for building a facts-only, source-cited, RAG-based Q&A assistant. 

**Goal:** A compliant, verifiable assistant for HDFC mutual fund schemes using a closed corpus from Groww.
**Iteration Scope:** Strictly limited to the 5 Groww HDFC scheme URLs listed in Phase 0. No other URLs (AMC PDFs, AMFI, SEBI) are ingested or cited.

---

## 1. Architectural Principles
These principles drive every phase of the implementation:

1.  **Facts-over-Intelligence**: Retrieval grounds every answer. The **Groq-hosted generation model** (Llama-3) only reformats retrieved facts.
2.  **Single Source of Truth**: Exactly one citation URL per response, matching the source of the fact.
3.  **Closed Corpus**: Only whitelisted URLs are ingested. Non-whitelisted links are blocked by a CI compliance gate.
4.  **Refusal by Default**: Advisory, opinion, or comparison queries are deflected with a polite redirect.
5.  **PII-Free**: No PAN, Aadhaar, account numbers, or contact details are processed or logged.
6.  **Determinism > Creativity**: Low temperature (0.0), strict prompt contracts, and hard answer caps (≤ 3 sentences).
7.  **Auditability**: Every response is traceable to a chunk, a document, a source URL, and a "last updated" timestamp.

---

## Phase 0: Foundation & Governance
**Goal:** Lock down scope, sources, and guardrails before writing code.

### 0.1 Governance Files
- **`config/sources.yaml`**: The definitive registry of the 5 HDFC Groww URLs.
- **`config/refusal_intents.yaml`**: Patterns and canned refusal copy for advisory queries.
- **`config/disclaimer.txt`**: "Facts-only. No investment advice."
- **`config/pii_deny_list.yaml`**: Regex patterns for redacting sensitive user data.

### 0.2 Whitelisted Corpus (Strict)
| # | Scheme Name | Category | Source URL (Groww) |
| :--- | :--- | :--- | :--- |
| 1 | HDFC Mid Cap Fund | Mid Cap | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 2 | HDFC Flexi Cap Fund | Flexi Cap | [Link](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| 3 | HDFC Focused 30 Fund | Focused | [Link](https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth) |
| 4 | HDFC ELSS Tax Saver | ELSS | [Link](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth) |
| 5 | HDFC Top 100 Fund | Large Cap | [Link](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |

---

## Phase 1: Ingestion & Corpus Build (Offline Pipeline)
**Goal:** Convert the 5 whitelisted URLs into a clean, embedded, and indexed corpus.

### Sub-phase 1.1 — Fetcher
- **Purpose**: Pull the 5 Groww HTML pages and persist raw snapshots.
- **Input**: `config/sources.yaml`.
- **Output**: `data/raw/<scheme_id>/<timestamp>.html` + `meta.json` ({url, fetched_at, content_hash_raw}).
- **Module**: `src/mf_faq/ingestion/fetcher.py`.
- **Behavior**: Use `httpx` with a Playwright fallback for JS-heavy sections. Respect `robots.txt`.
- **Exit Criteria**: All 5 URLs fetched; raw files ≥ minimum size; `meta.json` present.

### Sub-phase 1.2 — Extractor
- **Purpose**: HTML → structured text with section anchors (Expense Ratio, Exit Load, etc.).
- **Input**: Raw HTML files from 1.1.
- **Output**: `data/processed/<scheme_id>/extracted.json`.
- **Module**: `src/mf_faq/ingestion/extractor.py`.
- **Behavior**: Use `trafilatura` + targeted CSS selectors for must-have anchors.
- **Exit Criteria**: Extracted JSON exists for all 5 schemes; ≥ 4 must-have anchors present per page.

### Sub-phase 1.3 — Cleaner & Normalizer
- **Purpose**: Strip boilerplate and normalize encoding.
- **Input**: Extracted JSON from 1.2.
- **Output**: `data/processed/<scheme_id>/cleaned.json`.
- **Module**: `src/mf_faq/ingestion/cleaner.py`.
- **Behavior**: NFKC normalization; map Rs./INR → ₹; strip generic FAQ sections and boilerplate.
- **Exit Criteria**: Cleaned text contains zero boilerplate; Fund Manager/House sections contain no bios or contact details.

### Sub-phase 1.4 — Chunker
- **Purpose**: Hybrid section-aware splitting into retrieval units with context injection.
- **Input**: Cleaned JSON from 1.3.
- **Output**: `data/processed/<scheme_id>/chunks.jsonl`.
- **Module**: `src/mf_faq/ingestion/chunker.py`.
- **Behavior**: 
    - **Atomic Chunks**: Generate 1-2 chunks for key stats (NAV, Exp. Ratio, Min Inv) with explicit label-value formatting.
    - **Table-Aware splitting**: Identify Markdown tables in `full_text_summary` and ensure rows are not separated from headers.
    - **Context Injection**: Every chunk MUST start with the scheme name: `Fund: <name>\nSection: <type>\n<content>`.
    - **Size**: Soft cap 300 tokens; hard cap 500.
- **Exit Criteria**: Total chunk count 10–20 per scheme; no orphaned table rows; 100% chunks have fund name context.

### Sub-phase 1.5 — Embedder
- **Purpose**: Generate dense vectors per chunk.
- **Input**: Chunks from 1.4.
- **Output**: `data/index/embeddings.parquet` + `embedder.json`.
- **Module**: `src/mf_faq/ingestion/embedder.py`.
- **Behavior**: Embed `f"{scheme_name}\n\n{text}"` using `bge-small-en`.
- **Exit Criteria**: Every chunk has one 384-dim embedding; `embedder.json` present.

### Sub-phase 1.6 — Indexer
- **Purpose**: Build Dense (FAISS) + BM25 indexes.
- **Input**: Chunks (1.4) + Embeddings (1.5).
- **Output**: `data/index/vector.faiss`, `bm25.pkl`, and `manifest.json`.
- **Module**: `src/mf_faq/ingestion/indexer.py`.
- **Behavior**: Atomic swap: build in `.staging/` then rename.
- **Exit Criteria**: Retriever can load the index and run a sample query; manifest chunk count matches store.

### Sub-phase 1.7 — Refresh Orchestrator (Automation)
- **Purpose**: Automate the end-to-end pipeline (1.1 → 1.6) for daily data freshness.
- **Infrastructure**: **GitHub Actions** (Workflow scheduler).
- **Module**: `src/mf_faq/ingestion/refresh.py`.
- **Behavior**: 
    - Trigger: Cron schedule (Daily 10:00 AM IST / 04:30 UTC) or Manual Dispatch.
    - Execution: Sequential run of Fetcher, Extractor, Cleaner, Chunker, and Indexer.
    - Data Persistence: Commits updated index files to the repository to keep the production RAG fresh.
- **Exit Criteria**: `.github/workflows/daily_ingestion.yml` functional; `refresh.py` executes full cycle in < 5 mins.

---

## Phase 2: Retrieval Layer
**Goal:** Surface the minimum set of chunks needed to answer factually with 100% fund-context accuracy.

### Sub-phase 2.1 — Scheme Resolver
- **Purpose**: Identify which of the 5 funds the user is asking about.
- **Mechanism**: Keyword mapping (e.g., "ELSS" -> `hdfc_elss`, "Mid Cap" -> `hdfc_mid_cap`).
- **Behavior**: If no scheme is detected, default to multi-scheme search or ask for clarification.

### Sub-phase 2.2 — Filtered Retrieval
- **Purpose**: Execute BM25 search within the scope of the resolved scheme.
- **Mechanism**: Restricted BM25 scores (only consider chunks where `scheme_id` matches).
- **Behavior**: Retrieve top 3-5 chunks.

### Sub-phase 2.3 — Confidence Guardrail
- **Purpose**: Prevent hallucinations by refusing low-quality matches.
- **Mechanism**: Score thresholding (e.g., `score > 2.0`).
- **Behavior**: Return "No relevant facts found" if confidence is low.

### Sub-phase 2.4 — Context Formatter
- **Purpose**: Prepare the retrieved chunks for the Orchestrator.
- **Output**: Cleaned text block with metadata: `[Source: <url>] Fund: <name> | <content>`.
- **Confidence Gate**: If top rerank score < threshold, trigger "I don't know" path.

---

## Phase 3: Reasoning Engine (Generation)
**Goal:** Generate deterministic, facts-only responses with single-source citations.

### Sub-phase 3.1 — Prompt Engineering
- **System Prompt**: Enforce "Refusal by Default" for non-corpus queries.
- **Rules**: 
    - Use ONLY provided context.
    - Determinism: Temperature = 0.0.
    - Citation: Exactly one source URL per factual answer.

### Sub-phase 3.2 — PII & Refusal Guardrails
- **Refusal Logic**: If context is insufficient, respond with "I'm sorry, I don't have that information."
- **No-Source for Refusal**: **IMPORTANT**: If an answer is NOT found, DO NOT attach any source URLs or links.
- **PII Scrubbing**: Redact/Block inputs with PAN, Aadhaar, phone numbers, or emails from the final output.

### Sub-phase 3.3 — LLM (Answer Generator) Groq
- **Model**: Groq (Llama-3-8b or 70b).
- **Behavior**: Wrap Retriever + LLM into a unified `generate_answer(query)` function.
- **Exit Criteria**: 100% factual accuracy; unknowns trigger no-source refusal; zero PII leakage.

---

## Phase 4: User Interface (Next.js)
**Goal:** A clean, trustworthy entry point with a high-fidelity "Premium Stitch" design.

- **Framework**: Next.js (React) + Tailwind CSS + Framer Motion.
- **UX Rules**: Persistent facts-only disclaimer, example queries, responsive chat interface, and clickable citations.
- **Minimalist Approach**: Prioritizing transparency and accessibility over unnecessary complexity.

---

## Phase 5: Production Backend API (FastAPI)
**Goal:** Decouple the reasoning logic into a scalable REST API.

- **Framework**: FastAPI (Python).
- **Security**: Strict CORS policies allowing only the Vercel frontend origin.
- **Performance**: Asynchronous endpoint handling (`async def chat`) with Uvicorn.
- **Observability**: Structured logging for query monitoring and RAG latency tracking.

---

## Phase 6: Decoupled Deployment (Render & Vercel)
**Goal:** Professional, scalable hosting with automated CI/CD.

### 6.1 Backend on Render
- **Infrastructure**: Web Service (Dockerized).
- **Data Persistence**: BM25 index and processed data committed to Git for instant retrieval.
- **Automation**: GitHub Actions periodically triggers `refresh.py` and commits index updates, which Render picks up via auto-deploy.
- **Scaling**: Configured for 256MB/512MB RAM (Low footprint).

### 6.2 Frontend on Vercel
- **Infrastructure**: Vercel Edge Network.
- **Build Settings**: Next.js production build with environment-specific API endpoints.
- **Integration**: Secure communication with Render backend via encrypted environment variables.

---

## Phase 7: Evaluation & Compliance
**Goal:** Prove accuracy and safety via CI gates.

- **Factual Suite**: 30+ Qs with gold answers (90% pass bar).
- **Refusal Suite**: Ensure advisory queries never get a factual answer.
- **CI Gate**: Fail build if any generated answer cites a URL outside the Phase 0 whitelist.
- **Log Scanner**: Ensure raw queries with PII never hit persistent logs.
