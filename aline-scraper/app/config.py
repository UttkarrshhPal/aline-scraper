# Configuration management placeholder 

import os
from dotenv import load_dotenv
import yaml

class Config:
    def __init__(self, env_path: str = '.env', scraping_rules_path: str = '../config/scraping_rules.yaml'):
        # Load environment variables
        load_dotenv(env_path)
        self.database_url = os.getenv('DATABASE_URL')
        self.redis_url = os.getenv('REDIS_URL')
        self.request_delay = float(os.getenv('REQUEST_DELAY', 1.0))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.timeout_seconds = int(os.getenv('TIMEOUT_SECONDS', 30))
        self.max_concurrent_jobs = int(os.getenv('MAX_CONCURRENT_JOBS', 5))
        self.max_pdf_size_mb = int(os.getenv('MAX_PDF_SIZE_MB', 50))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 150))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_format = os.getenv('LOG_FORMAT', 'json')

        # Load scraping rules YAML
        self.scraping_rules = self._load_scraping_rules(scraping_rules_path)

    def _load_scraping_rules(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return {} 