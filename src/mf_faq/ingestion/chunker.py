import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chunker:
    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = Path(processed_dir)

    def create_atomic_chunks(self, data: dict, scheme_name: str) -> list:
        chunks = []
        
        # 1. Core Stats Chunk
        stats_text = (
            f"Fund: {scheme_name}\n"
            f"Section: Key Statistics\n"
            f"NAV: {data.get('nav', 'N/A')}\n"
            f"Expense Ratio: {data.get('expense_ratio', 'N/A')}\n"
            f"Fund Size (AUM): {data.get('fund_size_(aum)', 'N/A')}\n"
            f"Rating: {data.get('rating', 'N/A')}"
        )
        chunks.append({
            "content": stats_text,
            "section": "key_stats",
            "type": "atomic"
        })

        # 2. Minimum Investment Chunk
        min_inv = data.get("minimum_investments", {})
        if min_inv:
            inv_text = f"Fund: {scheme_name}\nSection: Minimum Investment Details\n"
            inv_text += "\n".join([f"{k}: {v}" for k, v in min_inv.items()])
            chunks.append({
                "content": inv_text,
                "section": "min_investment",
                "type": "atomic"
            })
        
        # 3. Exit Load / Tax Sections
        for key in ["exit_load_section", "taxability_section", "stamp_duty_section"]:
            if key in data and data[key]:
                section_name = key.replace("_", " ").title()
                chunks.append({
                    "content": f"Fund: {scheme_name}\nSection: {section_name}\n{data[key]}",
                    "section": key,
                    "type": "atomic"
                })

        return chunks

    def create_semantic_chunks(self, data: dict, scheme_name: str, char_limit: int = 500) -> list:
        full_text = data.get("full_text_summary", "")
        if not full_text:
            return []

        lines = full_text.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If adding this line exceeds limit, and we already have content, flush
            if current_size + len(line) > char_limit and current_chunk:
                content = f"Fund: {scheme_name}\nSection: Fund Details\n" + "\n".join(current_chunk)
                chunks.append({
                    "content": content,
                    "section": "general",
                    "type": "semantic"
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += len(line)

        # Final flush
        if current_chunk:
            content = f"Fund: {scheme_name}\nSection: Fund Details\n" + "\n".join(current_chunk)
            chunks.append({
                "content": content,
                "section": "general",
                "type": "semantic"
            })
            
        return chunks

    def process_scheme(self, scheme_id: str):
        scheme_dir = self.processed_dir / scheme_id
        cleaned_path = scheme_dir / "cleaned.json"
        
        if not cleaned_path.exists():
            logger.warning(f"No cleaned.json found for {scheme_id}")
            return False

        logger.info(f"Chunking {scheme_id}")
        with open(cleaned_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scheme_name = data.get("fund_name", scheme_id)
        
        all_chunks = []
        all_chunks.extend(self.create_atomic_chunks(data, scheme_name))
        all_chunks.extend(self.create_semantic_chunks(data, scheme_name))
        
        # Save as JSONL
        out_path = scheme_dir / "chunks.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for idx, chunk in enumerate(all_chunks):
                chunk_meta = {
                    "scheme_id": scheme_id,
                    "chunk_id": f"{scheme_id}_{idx}",
                    **chunk
                }
                f.write(json.dumps(chunk_meta) + "\n")
        
        return len(all_chunks)

    def process_all(self):
        scheme_ids = [d.name for d in self.processed_dir.iterdir() if d.is_dir()]
        results = {}
        for sid in scheme_ids:
            count = self.process_scheme(sid)
            results[sid] = f"success ({count} chunks)" if count else "failed"
        return results

if __name__ == "__main__":
    chunker = Chunker()
    report = chunker.process_all()
    print(json.dumps(report, indent=2))
