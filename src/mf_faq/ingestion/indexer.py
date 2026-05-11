import os
import json
import logging
import pickle
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Indexer:
    """
    Unified Search Interface.
    Currently implements Sparse Search (BM25) as a fallback for dense embeddings.
    Designed to be easily upgraded to Hybrid Search (Dense + Sparse).
    """
    def __init__(self, index_dir: str = "data/index"):
        self.index_dir = Path(index_dir)
        self.index_path = self.index_dir / "bm25_index.pkl"
        self.data = None
        self.bm25 = None
        self.chunks = None

    def load(self):
        if not self.index_path.exists():
            logger.error(f"Index file not found at {self.index_path}. Run embedder first.")
            return False
        
        with open(self.index_path, "rb") as f:
            self.data = pickle.load(f)
            self.bm25 = self.data["bm25_model"]
            self.chunks = self.data["chunks"]
        
        logger.info(f"Loaded BM25 index with {len(self.chunks)} chunks.")
        return True

    def tokenize(self, text: str):
        return text.lower().split()

    def search(self, query: str, top_k: int = 3) -> list:
        if not self.bm25:
            if not self.load():
                return []

        tokenized_query = self.tokenize(query)
        # Get scores for all chunks
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top_k indices
        import numpy as np
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0: # Only return chunks with some relevance
                results.append({
                    "chunk": self.chunks[idx],
                    "score": float(scores[idx])
                })
        
        return results

if __name__ == "__main__":
    indexer = Indexer()
    if indexer.load():
        # Test Queries
        test_queries = [
            "HDFC Mid Cap Fund NAV",
            "What is the expense ratio of HDFC ELSS?",
            "Minimum SIP for Large Cap",
            "Exit load for focused fund"
        ]
        
        for q in test_queries:
            print(f"\nQuery: {q}")
            results = indexer.search(q, top_k=2)
            for r in results:
                print(f"[{r['score']:.2f}] {r['chunk']['scheme_id']} | {r['chunk']['section']}")
                # print(f"Content: {r['chunk']['content'][:100]}...")
