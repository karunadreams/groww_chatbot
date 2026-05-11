import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import os
import shutil
from src.mf_faq.ingestion.fetcher import Fetcher

class TestFetcher(unittest.TestCase):
    def setUp(self):
        self.test_config = "config/sources.yaml"
        self.test_data_dir = "data/test_raw"
        self.fetcher = Fetcher(config_path=self.test_config, base_data_dir=self.test_data_dir)

    def tearDown(self):
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    @patch("httpx.AsyncClient.get")
    async def test_fetch_with_httpx_success(self, mock_get):
        # Mocking the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Expense Ratio: 1.1%</body></html>"
        mock_get.return_value = mock_response

        content = await self.fetcher.fetch_with_httpx("https://example.com")
        self.assertIn("Expense Ratio", content)

    def test_load_sources(self):
        sources = self.fetcher._load_sources()
        self.assertEqual(len(sources), 5)
        self.assertEqual(sources[0]["id"], "hdfc_mid_cap")

    def test_content_hash(self):
        content = "test content"
        h1 = self.fetcher._get_content_hash(content)
        h2 = self.fetcher._get_content_hash(content)
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, self.fetcher._get_content_hash("other"))

if __name__ == "__main__":
    unittest.main()
