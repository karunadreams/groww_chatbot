import os
import re
import logging
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv
from src.mf_faq.retrieval.retriever import Retriever

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReasoningEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. Generation will fail.")
        
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.retriever = Retriever()
        
        # Load sources for citation mapping
        import yaml
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        config_path = os.path.join(root_dir, "config", "sources.yaml")
        with open(config_path, "r") as f:
            sources_data = yaml.safe_load(f)
            self.source_map = {s["id"]: s["sources"][0]["url"] for s in sources_data["schemes"]}

    def _scrub_pii(self, text: str) -> str:
        """Simple regex-based PII scrubbing."""
        # Phone numbers
        text = re.sub(r"\b\d{10}\b", "[REDACTED]", text)
        # Emails
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED]", text)
        # PAN/Aadhaar (rough patterns)
        text = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", "[REDACTED]", text)
        return text

    def generate_answer(self, query: str) -> Dict:
        """End-to-end generation with refusal and citation logic."""
        # 1. Retrieve
        results = self.retriever.retrieve(query)
        # 2. Generate with LLM
        context = self.retriever.format_context(results) if results else "No fund-specific data found for this query."
        system_prompt = (
            "You are a Facts-Only Mutual Fund Assistant for HDFC Mutual Funds. "
            "STRICT POLICIES:\n"
            "1. NO ADVICE: Refuse queries like 'Should I invest?' or 'Which is better?'. "
            "   Response MUST include exactly this link: https://www.amfiindia.com/investor-corner/educational-material\n"
            "2. NO PERFORMANCE: Do not provide return calculations. If asked about returns, "
            "   Response MUST include exactly this link: https://www.hdfcfund.com/information/factsheet\n"
            "3. FACTS ONLY: Only answer about Expense Ratio, Exit Load, Min SIP, ELSS lock-in, Riskometer, or Benchmark. "
            "   If the context does not contain the answer or the query is off-topic, respond EXACTLY with: "
            "   'I don't have a verified answer for that. Please specify which scheme: HDFC Mid Cap, HDFC Equity (Flexi Cap), HDFC Focused, HDFC ELSS Tax Saver, or HDFC Large Cap.' "
            "   In this case, DO NOT include any links or footers.\n"
            "4. RESPONSE FORMAT:\n"
            "   - Max 3 sentences.\n"
            "   - For factual answers, include exactly ONE relevant link (SOURCE URL) and exactly this Footer: 'Last updated from sources: [Data as of date from context]'.\n"
            "   - For refusals, NO links and NO footer.\n"
            "5. ALIASES: 'Focused 30' = HDFC Focused Fund, 'Top 100' = HDFC Large Cap, 'Flexi Cap' = HDFC Equity Fund."
        )
        
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        
        if not self.client:
            return {"answer": "[MOCK] " + (results[0]["chunk"]["content"][:200]), "source": self.source_map.get(results[0]["chunk"]["scheme_id"])}

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0
            )
            answer = chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Generation failed for query '{query}': {str(e)}", exc_info=True)
            answer = "I'm sorry, I encountered an error while processing your request. Please check the backend logs."

        # 3. Apply Refusal Policy for Source
        refusal_phrases = ["don't have that information", "not mentioned in the context", "sorry", "i don't have a verified answer"]
        is_refusal = any(p in answer.lower() for p in refusal_phrases)
        
        # 4. Scrub PII
        answer = self._scrub_pii(answer)
        
        # 5. Attach Source
        source_url = None
        if not is_refusal and results:
            # Get the primary scheme ID from the top result
            primary_scheme = results[0]["chunk"]["scheme_id"]
            source_url = self.source_map.get(primary_scheme)

        return {
            "answer": answer,
            "source": source_url
        }

if __name__ == "__main__":
    # Test
    engine = ReasoningEngine()
    test_queries = [
        "What is the NAV of HDFC Mid Cap?",
        "Who is the current Prime Minister?",
        "My phone number is 9876543210, can you help me?"
    ]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        res = engine.generate_answer(q)
        print(f"Answer: {res['answer']}")
        print(f"Source: {res['source']}")
