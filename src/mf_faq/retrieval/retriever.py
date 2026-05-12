import logging
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from src.mf_faq.ingestion.indexer import Indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, index_dir: str = "data/index"):
        self.indexer = Indexer(index_dir)
        self.indexer.load()
        
        # Load sources from config
        config_path = Path("config/sources.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                sources_data = yaml.safe_load(f)
                self.source_map = {s["id"]: s["sources"][0]["url"] for s in sources_data["schemes"]}
        else:
            self.source_map = {}

        # Scheme mapping for resolution
        self.scheme_keywords = {
            "hdfc_elss": ["elss", "tax saver", "tax saving", "tax"],
            "hdfc_equity": ["equity", "multi cap", "multi-cap", "flexi cap", "flexi-cap", "flexicap"],
            "hdfc_focused": ["focused", "focus", "focused 30", "focus 30"],
            "hdfc_large_cap": ["large cap", "large-cap", "bluechip", "top 100", "top-100", "largecap"],
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

    def retrieve(self, query: str, top_k: int = 10, threshold: float = 0.3) -> List[Dict]:
        """Unified retrieval pipeline with scheme filtering and thresholding."""
        resolved_schemes = self.resolve_schemes(query)
        
        # Search using the Indexer
        # Get more chunks initially to ensure we have enough after filtering
        raw_results = self.indexer.search(query, top_k=30) 
        
        filtered_results = []
        for res in raw_results:
            chunk = res["chunk"]
            score = res["score"]
            
            # Confidence Guardrail (Low threshold for high recall)
            if score < threshold:
                continue
                
            # Scheme Filtering (Optional)
            if resolved_schemes:
                if chunk["scheme_id"] not in resolved_schemes:
                    continue

            # BOOST: Atomic chunks (like Key Stats) are often shorter but high-value
            if chunk.get("type") == "atomic":
                score *= 1.5
            
            filtered_results.append({"chunk": chunk, "score": score})
            
        # Sort by boosted score
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_k]

    def format_context(self, results: List[Dict]) -> str:
        """Formats results into a single context string for the LLM."""
        if not results:
            return "No relevant facts found in the mutual fund corpus."
            
        context_blocks = []
        for res in results:
            chunk = res["chunk"]
            source_url = self.source_map.get(chunk['scheme_id'], "N/A")
            block = (
                f"--- SCHEME: {chunk['scheme_id'].upper()} ---\n"
                f"SOURCE URL: {source_url}\n"
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
