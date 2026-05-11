# Edge Cases & Failure Modes: Mutual Fund FAQ Assistant

This document identifies edge cases categorized by their corresponding architectural phase, ensuring robust handling of extraction, retrieval, and compliance risks.

---

## Phase 1: Ingestion & Corpus Build

| ID | Edge Case | Architectural Mitigation (Phase) |
| :--- | :--- | :--- |
| **EC-1.1** | **Anti-Bot Trigger** | Use `playwright` with realistic User-Agents; respect `robots.txt` and ETag 304 headers (1.1). |
| **EC-1.2** | **Soft-404 Detection** | Verify presence of "must-have" anchors (Expense Ratio/Exit Load) after fetch; fail if missing (1.2). |
| **EC-1.3** | **Dynamic Table Load** | Wait for `aria-expanded="false"` accordions to load and expand before extraction (1.2). |
| **EC-1.4** | **Boilerplate Leak** | Strip specific CSS classes associated with "Similar Funds" or "Recommended" ads (1.3). |
| **EC-1.5** | **Numeric Normalization** | Normalize "Rs. 500", "INR 500", and "₹500" into a single canonical format (1.3). |
| **EC-1.6** | **Near-Duplicate Chunks** | Prepend `scheme_name` to text before embedding to differentiate identical "Exit Load" sections across funds (1.5). |
| **EC-1.7** | **Atomic Row Split** | Ensure chunking logic never splits a "Parameter: Value" pair (e.g., "Min SIP: ₹500") across chunks (1.4). |
| **EC-1.8** | **Content Hash Drift** | Trigger a "Freeze" alert if > 2 fund pages change content significantly in a single night (1.7). |

---

## Phase 2: Retrieval Layer

| ID | Edge Case | Architectural Mitigation (Phase) |
| :--- | :--- | :--- |
| **EC-2.1** | **Term Mismatch** | Use Hybrid Search (BM25 + Dense) to catch exact numeric facts that semantic search might miss (2.1). |
| **EC-2.2** | **Scheme Ambiguity** | If query is "What is the fee?", use Scheme Resolver to ask "Which fund?" or default to the most relevant context (2.1). |
| **EC-2.3** | **Tokenization Gap** | Normalize acronyms (ELSS → Equity Linked Savings Scheme) in the query before search (2.1). |
| **EC-2.4** | **Low-Confidence Hit** | Set a cross-encoder threshold; if rerank score < 0.6, route to "I don't know" path (2.2). |

---

## Phase 3: Reasoning & Guardrails

| ID | Edge Case | Architectural Mitigation (Phase) |
| :--- | :--- | :--- |
| **EC-3.1** | **PII Injection** | Regex-based PII Guard scans input *before* it hits the retriever or LLM (3.1). |
| **EC-3.2** | **Advisory Intent** | Classifier flags "Should I buy?" and routes to Refusal Composer with educational link (3.1). |
| **EC-3.3** | **Hallucinated URLs** | Post-processor regex-scans output; rejects any reply citing a domain not in the Phase 0 whitelist (3.2). |
| **EC-3.4** | **Sentence Overflow** | Hard truncation or LLM re-prompt if answer exceeds the 3-sentence limit (3.2). |
| **EC-3.5** | **Banned Tokens** | Scanner blocks words like "recommend", "advice", "guaranteed", or "outperform" (3.2). |

---

## Phase 4 & 5: UI & Compliance

| ID | Edge Case | Architectural Mitigation (Phase) |
| :--- | :--- | :--- |
| **EC-4.1** | **Broken Citation** | UI validates that the citation URL string-matches one of the 5 whitelisted URLs (4.1). |
| **EC-5.1** | **Regression** | Factual Suite (30 Qs) runs in CI; build fails if accuracy drops below 90% (5.1). |
| **EC-5.2** | **PII in Logs** | Automated log scanner alerts if any pattern matching a PAN or Email appears in structured logs (5.2). |
