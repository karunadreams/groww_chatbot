import os
import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup
import trafilatura

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)

    def _get_latest_snapshot(self, scheme_id: str) -> Path:
        scheme_dir = self.raw_dir / scheme_id
        if not scheme_dir.exists():
            return None
        
        snapshots = list(scheme_dir.glob("*.html"))
        if not snapshots:
            return None
        
        # Return the most recent by filename (timestamp format)
        return max(snapshots)

    def extract_fields(self, html_content: str) -> dict:
        soup = BeautifulSoup(html_content, "html.parser")
        data = {}

        # 1. Basic Info
        title_tag = soup.find("h1")
        data["fund_name"] = title_tag.text.strip() if title_tag else "Unknown"

        # 2. Key Stats (NAV, Expense Ratio, etc.)
        stats_container = soup.find("div", class_=lambda x: x and "fundDetails_fundDetailsContainer" in x)
        if stats_container:
            # Capture "NAV: 08 May '26"
            nav_date_div = stats_container.find("div", string=lambda x: x and "NAV:" in x)
            if nav_date_div:
                data["as_of_date"] = nav_date_div.text.replace("NAV:", "").strip()
            
            stats = stats_container.find_all("div", recursive=False)
            for stat in stats:
                label_div = stat.find("div", class_=lambda x: x and "contentTertiary" in x)
                value_div = stat.find("div", class_=lambda x: x and "contentPrimary" in x)
                if label_div and value_div:
                    label = label_div.text.split(":")[0].strip().lower().replace(" ", "_")
                    value = value_div.text.strip()
                    data[label] = value

        # 3. Minimum Investments
        min_inv_section = soup.find("h3", string=lambda x: x and "Minimum investments" in x)
        if min_inv_section:
            container = min_inv_section.find_parent("div")
            rows = container.find_all("div", class_="vspace-between")
            min_inv = {}
            for row in rows:
                label = row.find("div", class_="contentSecondary").text.strip()
                value = row.find("div", class_="bodyBaseHeavy").text.strip()
                min_inv[label] = value
            data["minimum_investments"] = min_inv

        # 4. Exit Load & Tax & Lock-in
        for section_title in ["Exit load", "Taxability", "Stamp duty", "Lock-in"]:
            # Check h1-h6 for section headers
            header = soup.find(lambda tag: tag.name in ["h2", "h3", "h4", "h5", "h6"] and section_title.lower() in tag.text.lower())
            if header:
                container = header.find_parent("div")
                if container:
                    content = container.get_text(separator=" ", strip=True)
                    # Clean the key: replace space with underscore
                    key_name = f"{section_title.lower().replace(' ', '_').replace('-', '_')}_section"
                    data[key_name] = content
            else:
                # Fallback: Search for specific semantic spans
                keyword_tag = soup.find(string=lambda x: x and section_title.lower() in x.lower())
                if keyword_tag:
                    parent = keyword_tag.find_parent(["div", "p", "span"])
                    if parent:
                        data[f"{section_title.lower().replace(' ', '_')}_fallback"] = parent.get_text(strip=True)

        # 5. Specialized Check for ELSS Lock-in
        if "elss" in data.get("fund_name", "").lower():
            lockin_span = soup.find("span", string=lambda x: x and "lock-in" in x.lower())
            if lockin_span:
                data["lock_in_period"] = lockin_span.get_text(strip=True)
            elif "3y lock-in" in html_content.lower():
                data["lock_in_period"] = "3 years (standard for ELSS)"

        # 5. Broad Text Extraction using Trafilatura
        # Trafilatura is great for fallback but we want to ensure table data is preserved
        trafilatura_text = trafilatura.extract(html_content, include_tables=True, include_links=False)
        data["full_text_summary"] = trafilatura_text

        return data

    def process_scheme(self, scheme_id: str):
        snapshot_path = self._get_latest_snapshot(scheme_id)
        if not snapshot_path:
            logger.warning(f"No snapshot found for {scheme_id}")
            return False

        logger.info(f"Extracting {scheme_id} from {snapshot_path.name}")
        with open(snapshot_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        extracted_data = self.extract_fields(html_content)
        
        # Save output
        out_dir = self.processed_dir / scheme_id
        out_dir.mkdir(parents=True, exist_ok=True)
        
        out_path = out_dir / "extracted.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=4)
        
        return True

    def process_all(self):
        scheme_ids = [d.name for d in self.raw_dir.iterdir() if d.is_dir()]
        results = {}
        for sid in scheme_ids:
            success = self.process_scheme(sid)
            results[sid] = "success" if success else "failed"
        return results

if __name__ == "__main__":
    extractor = Extractor()
    report = extractor.process_all()
    print(json.dumps(report, indent=2))
