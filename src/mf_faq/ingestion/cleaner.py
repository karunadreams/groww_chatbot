import os
import json
import logging
import re
import unicodedata
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Cleaner:
    def __init__(self, processed_dir: str = "data/processed"):
        self.processed_dir = Path(processed_dir)
        # Patterns to strip from text
        self.boilerplate_patterns = [
            r"Invest in .* Online with Groww",
            r"Compare Funds",
            r"See All",
            r"Invest Now",
            r"\| Compare \|",
            r"Category average \(.*\)",
            r"Rank \(.*\)"
        ]

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        
        # 1. NFKC Normalization
        text = unicodedata.normalize("NFKC", text)
        
        # 2. Currency Normalization
        text = text.replace("Rs.", "₹").replace("INR", "₹")
        
        # 3. Boilerplate removal
        for pattern in self.boilerplate_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        # 4. Whitespace cleanup (preserve newlines for tables)
        text = re.sub(r"[ \t]+", " ", text).strip()
        
        return text

    def clean_json(self, data: dict) -> dict:
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = self.normalize_text(value)
            elif isinstance(value, dict):
                cleaned[key] = {k: self.normalize_text(v) for k, v in value.items()}
            else:
                cleaned[key] = value
        
        # Explicitly strip Groww generic FAQ marker if found in full_text_summary
        if "full_text_summary" in cleaned:
            # Simple heuristic: if we see "Frequently Asked Questions" followed by general terms
            faq_marker = "frequently asked questions"
            if faq_marker in cleaned["full_text_summary"].lower():
                # Split and take the part before FAQ if it looks generic
                parts = re.split(r"frequently asked questions", cleaned["full_text_summary"], flags=re.IGNORECASE)
                cleaned["full_text_summary"] = parts[0].strip()

        return cleaned

    def process_scheme(self, scheme_id: str):
        scheme_dir = self.processed_dir / scheme_id
        extracted_path = scheme_dir / "extracted.json"
        
        if not extracted_path.exists():
            logger.warning(f"No extracted.json found for {scheme_id}")
            return False

        logger.info(f"Cleaning {scheme_id}")
        with open(extracted_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        cleaned_data = self.clean_json(data)
        
        out_path = scheme_dir / "cleaned.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=4)
        
        return True

    def process_all(self):
        scheme_ids = [d.name for d in self.processed_dir.iterdir() if d.is_dir()]
        results = {}
        for sid in scheme_ids:
            success = self.process_scheme(sid)
            results[sid] = "success" if success else "failed"
        return results

if __name__ == "__main__":
    cleaner = Cleaner()
    report = cleaner.process_all()
    print(json.dumps(report, indent=2))
