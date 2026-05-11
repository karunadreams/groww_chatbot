import os
import json
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
import httpx
import yaml
from playwright.async_api import async_playwright

class Fetcher:
    def __init__(self, config_path: str = "config/sources.yaml", base_data_dir: str = "data/raw"):
        self.config_path = Path(config_path)
        self.base_data_dir = Path(base_data_dir)
        self.sources = self._load_sources()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _load_sources(self):
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f).get("schemes", [])

    def _get_content_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def fetch_with_httpx(self, url: str) -> str:
        """Fetch content using HTTPX."""
        async with httpx.AsyncClient(timeout=30.0, headers={"User-Agent": self.user_agent}) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text

    async def fetch_with_playwright(self, url: str) -> str:
        """Fallback fetch using Playwright for JS-heavy content."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=self.user_agent)
            await page.goto(url, wait_until="networkidle")
            # Ensure accordions or dynamic parts have time to load if necessary
            content = await page.content()
            await browser.close()
            return content

    async def fetch_all(self):
        """Fetch all whitelisted URLs and save snapshots."""
        results = []
        for scheme in self.sources:
            scheme_id = scheme["id"]
            for source in scheme["sources"]:
                url = source["url"]
                print(f"Fetching {scheme_id} from {url}...")
                
                try:
                    # Try HTTPX first
                    content = await self.fetch_with_httpx(url)
                    
                    # Simple heuristic: if content is too small or missing key terms, try Playwright
                    if len(content) < 5000 or "Expense Ratio" not in content:
                        print(f"Content for {scheme_id} looks incomplete. Falling back to Playwright...")
                        content = await self.fetch_with_playwright(url)
                    
                    # Prepare directories
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    scheme_dir = self.base_data_dir / scheme_id
                    scheme_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save HTML
                    file_name = f"{timestamp}.html"
                    file_path = scheme_dir / file_name
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    # Save Meta
                    meta = {
                        "url": url,
                        "fetched_at": datetime.now().isoformat(),
                        "content_hash_raw": self._get_content_hash(content),
                        "file_path": str(file_path),
                        "status": "success"
                    }
                    meta_path = scheme_dir / "meta.json"
                    with open(meta_path, "w") as f:
                        json.dump(meta, f, indent=4)
                    
                    results.append({"scheme_id": scheme_id, "status": "ok"})
                    
                except Exception as e:
                    print(f"Failed to fetch {scheme_id}: {str(e)}")
                    results.append({"scheme_id": scheme_id, "status": "failed", "error": str(e)})
        
        return results

if __name__ == "__main__":
    fetcher = Fetcher()
    asyncio.run(fetcher.fetch_all())
