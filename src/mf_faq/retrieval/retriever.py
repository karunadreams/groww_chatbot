import logging
import re
from typing import List, Dict, Optional
from src.mf_faq.ingestion.indexer import Indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, index_dir: str = "data/index"):
        self.indexer = Indexer(index_dir)
        self.indexer.load()
        
        # Scheme mapping for resolution
        self.scheme_keywords = {
            "hdfc_elss": ["elss", "tax saver", "tax saving", "tax"],
            "hdfc_equity": ["equity", "multi cap", "multi-cap"],
            "hdfc_focused": ["focused", "focus"],
            "hdfc_large_cap": ["large cap", "large-cap", "bluechip"],
            "hdfc_mid_cap": ["mid cap", "mid-cap", "middle"]
        }

    def resolve_schemes(self, query: str) -> List[str]:
        """Identifies which schemes are mentioned in the query."""
        query_lower = query.lower()
        resolved = []
        for scheme_id, keywords in self.scheme_keywords.items():
            if any(k in query_lower for k in keywords):
                resolved.append(scheme_id)
        return resolved

    def retrieve(self, query: str, top_k: int = 5, threshold: float = 1.5) -> List[Dict]:
        """Unified retrieval pipeline with scheme filtering and thresholding."""
        resolved_schemes = self.resolve_schemes(query)
        
        # Search using the Indexer
        # If schemes are resolved, we'll search across all but prioritize/filter later
        # (The Indexer doesn't have a filter param yet, so we filter here)
        raw_results = self.indexer.search(query, top_k=20) # Get more to filter
        
        filtered_results = []
        for res in raw_results:
            chunk = res["chunk"]
            score = res["score"]
            
            # Confidence Guardrail
            if score < threshold:
                continue
                
            # Scheme Filtering
            # If the user specified a scheme, only return chunks from that scheme
            if resolved_schemes and chunk["scheme_id"] not in resolved_schemes:
                continue
            
            filtered_results.append(res)
            
        # Sort and take top_k
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_k]

    def format_context(self, results: List[Dict]) -> str:
        """Formats results into a single context string for the LLM."""
        if not results:
            return "No relevant facts found in the mutual fund corpus."
            
        context_blocks = []
        for res in results:
            chunk = res["chunk"]
            block = (
                f"--- SCHEME: {chunk['scheme_id'].upper()} ---\n"
                f"SECTION: {chunk['section'].upper()}\n"
                f"{chunk['content']}\n"
            )
            context_blocks.append(block)
            
        return "\n".join(context_blocks)

if __name__ == "__main__":
    retriever = Retriever()
    
    # Test cases
    queries = [
        "What is the NAV of HDFC Mid Cap?",
        "Tell me about the exit load for ELSS fund",
        "Expense ratio of large cap vs focused fund",
        "Who is the manager?"
    ]
    
    for q in queries:
        print(f"\nQUERY: {q}")
        results = retriever.retrieve(q)
        context = retriever.format_context(results)
        print(f"RESULTS: {len(results)}")
        print(f"CONTEXT PREVIEW:\n{context[:200]}...")
