import logging
import sys
import time
from pathlib import Path
from src.mf_faq.ingestion.fetcher import Fetcher
from src.mf_faq.ingestion.extractor import Extractor
from src.mf_faq.ingestion.cleaner import Cleaner
from src.mf_faq.ingestion.chunker import Chunker
from src.mf_faq.ingestion.embedder import BM25Indexer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RefreshOrchestrator")

async def run_refresh(force: bool = False):
    start_time = time.time()
    logger.info("Starting Daily Ingestion Refresh Cycle...")

    try:
        # 1. Fetch
        logger.info("Step 1/5: Fetching latest snapshots...")
        fetcher = Fetcher()
        fetch_results = await fetcher.fetch_all()
        
        # Check for drift/changes
        # Heuristic: Compare the latest hash in meta.json with the previous one
        # For simplicity in this local version, we check if any 'success' was returned
        # and if the index exists.
        index_path = Path("data/index/bm25_index.pkl")
        
        # In a real production system, we'd compare hashes here.
        # For now, we'll proceed if anything was fetched or if index is missing.
        if not force and index_path.exists():
            logger.info("Index exists. Checking for content changes...")
            # Here we assume fetcher.fetch_all() would tell us if hashes changed
            # But since fetcher always overwrites meta.json, we'll just proceed
            # to ensure the index matches the latest data.
        
        # 2. Extract
        logger.info("Step 2/5: Extracting structured data...")
        extractor = Extractor()
        extractor.process_all()

        # 3. Clean
        logger.info("Step 3/5: Cleaning and normalizing...")
        cleaner = Cleaner()
        cleaner.process_all()

        # 4. Chunk
        logger.info("Step 4/5: Generating retrieval chunks...")
        chunker = Chunker()
        chunker.process_all()

        # 5. Index
        logger.info("Step 5/5: Rebuilding BM25 Search Index...")
        indexer = BM25Indexer()
        indexer.run()

        duration = time.time() - start_time
        logger.info(f"Refresh Cycle Completed Successfully in {duration:.2f} seconds.")
        return True

    except Exception as e:
        logger.error(f"Refresh Cycle Failed: {str(e)}")
        return False

import asyncio

if __name__ == "__main__":
    success = asyncio.run(run_refresh())
    if not success:
        sys.exit(1)
