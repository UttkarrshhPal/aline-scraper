# Aline Scraper

A scalable, production-ready content scraper for technical blogs, guides, and PDFs. Built with FastAPI, Celery, and modern Python tooling.

## Project Structure

```
aline-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── base.py             # Base scraper class
│   │   ├── blog_scraper.py     # Blog scraping logic
│   │   ├── pdf_processor.py    # PDF processing
│   │   ├── content_cleaner.py  # Content cleaning utilities
│   │   └── extractors.py       # Content extraction strategies
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── deps.py             # Dependencies
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py           # Database models
│   │   └── connection.py       # Database connection
│   └── utils/
│       ├── __init__.py
│       ├── logging.py          # Logging configuration
│       └── validators.py       # Data validation
├── config/
│   ├── scraping_rules.yaml     # Scraping configuration
│   └── logging.yaml            # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_scraping.py
│   ├── test_pdf.py
│   ├── test_api.py
│   └── fixtures/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
``` 