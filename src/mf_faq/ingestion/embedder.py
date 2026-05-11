import os
import json
import logging
import pickle
from pathlib import Path
from rank_bm25 import BM25Okapi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BM25Indexer:
    """
    Fallback indexer using BM25 (Sparse Search) to bypass DLL issues with dense embeddings.
    Provides keyword-accurate retrieval for facts like NAV, Expense Ratio, etc.
    """
    def __init__(self, processed_dir: str = "data/processed", index_dir: str = "data/index"):
        self.processed_dir = Path(processed_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def tokenize(self, text: str):
        # Simple whitespace tokenization with lowercasing
        # In production, we'd use a more robust tokenizer (like NLTK or SpaCy)
        return text.lower().split()

    def load_all_chunks(self) -> list:
        all_chunks = []
        for jsonl_file in self.processed_dir.glob("**/chunks.jsonl"):
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    all_chunks.append(json.loads(line))
        return all_chunks

    def run(self):
        chunks = self.load_all_chunks()
        if not chunks:
            logger.warning("No chunks found to index.")
            return

        logger.info(f"Building BM25 Index for {len(chunks)} chunks...")
        
        # Prepare corpus
        corpus = [c["content"] for c in chunks]
        tokenized_corpus = [self.tokenize(doc) for doc in corpus]
        
        # Initialize BM25
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Save BM25 object and chunks
        index_data = {
            "chunks": chunks,
            "bm25_model": bm25
        }
        
        out_path = self.index_dir / "bm25_index.pkl"
        with open(out_path, "wb") as f:
            pickle.dump(index_data, f)
            
        # Save Metadata for Phase 1.5 compliance
        meta = {
            "model_name": "BM25Okapi",
            "type": "sparse",
            "total_chunks": len(chunks),
            "created_at": str(Path(out_path).stat().st_mtime),
            "status": "DLL_FALLBACK_ACTIVE"
        }
        with open(self.index_dir / "embedder.json", "w") as f:
            json.dump(meta, f, indent=4)
        
        logger.info(f"BM25 Index saved to {out_path}")
        return meta

if __name__ == "__main__":
    indexer = BM25Indexer()
    report = indexer.run()
    if report:
        print(json.dumps(report, indent=2))
