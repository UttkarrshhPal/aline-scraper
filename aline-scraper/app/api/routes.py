from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from uuid import uuid4
from ..models import ScrapingRequest, ScrapeResponse, ScrapedItem
from app.scraping.blog_scraper import BlogScraper
from app.scraping.guide_scraper import GuideCollectionScraper
from app.scraping.extractors import DsaBlogScraper

router = APIRouter()

# Dummy in-memory job store for demonstration
jobs = {}

@router.post("/scrape")
def start_scrape(request: ScrapingRequest):
    job_id = str(uuid4())
    jobs[job_id] = {
        "status": "started",
        "progress": 0.0,
        "items_processed": 0,
        "total_items": 0,
        "errors": [],
        "results": None
    }
    results = []
    for source in request.sources:
        if source.type == "blog" and source.url:
            # Use DsaBlogScraper for nilmamano.com/category/dsa
            if "nilmamano.com/blog/category/dsa" in source.url:
                scraper = DsaBlogScraper()
                links = scraper.filter_category(source.url)
                for link in links:
                    content = scraper.extract_content_with_code_and_math(link)
                    content = scraper.detect_and_format_algorithms(content)
                    results.append({
                        "title": link,
                        "content": content,
                        "content_type": "blog",
                        "source_url": link,
                        "author": source.metadata.author if source.metadata else "",
                        "user_id": request.user_id
                    })
            else:
                scraper = BlogScraper()
                links = scraper.scrape_index(source.url)
                for link in links:
                    content = scraper.extract_content(link)
                    results.append({
                        "title": link,
                        "content": content,
                        "content_type": "blog",
                        "source_url": link,
                        "author": source.metadata.author if source.metadata else "",
                        "user_id": request.user_id
                    })
        elif source.type == "guide_collection" and source.url:
            guide_scraper = GuideCollectionScraper()
            guides = guide_scraper.extract_guides(source.url)
            for guide in guides:
                guide["user_id"] = request.user_id
                results.append(guide)
    jobs[job_id]["results"] = {"team_id": request.team_id, "items": results}
    return {
        "job_id": job_id,
        "status": "started",
        "estimated_completion": "2024-01-15T10:30:00Z"
    }

@router.get("/scrape/{job_id}/status")
def get_scrape_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"error": "Job not found"}
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "items_processed": job["items_processed"],
        "total_items": job["total_items"],
        "errors": job["errors"]
    }

@router.get("/scrape/{job_id}/results", response_model=ScrapeResponse)
def get_scrape_results(job_id: str):
    job = jobs.get(job_id)
    if not job or not job["results"]:
        return {"team_id": "", "items": []}
    return job["results"]

@router.post("/scrape/pdf")
def upload_pdf(
    file: UploadFile = File(...),
    team_id: str = Form('default-team'),
    user_id: str = Form('default-user'),
    max_chapters: int = Form(8)
):
    job_id = str(uuid4())
    jobs[job_id] = {
        "status": "started",
        "progress": 0.0,
        "items_processed": 0,
        "total_items": 0,
        "errors": [],
        "results": None
    }
    # Save uploaded file to disk
    import tempfile
    from app.scraping.pdf_processor import PdfProcessor
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        processor = PdfProcessor()
        chapters = processor.extract_chapters(tmp_path, max_chapters=max_chapters)
        items = []
        meta = processor.extract_metadata(tmp_path)
        for idx, chapter in enumerate(chapters):
            markdown = processor.preserve_markdown_format(chapter)
            chunks = processor.chunk_content(markdown)
            for chunk_idx, chunk in enumerate(chunks):
                items.append({
                    "title": f"{meta.get('title', file.filename)} - Chapter {idx+1} (Chunk {chunk_idx+1})",
                    "content": chunk,
                    "content_type": "book",
                    "source_url": file.filename,
                    "author": meta.get("author", ""),
                    "user_id": user_id
                })
        jobs[job_id]["results"] = {"team_id": team_id, "items": items}
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["items_processed"] = len(items)
        jobs[job_id]["total_items"] = len(items)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["errors"].append(str(e))
    finally:
        os.unlink(tmp_path)
    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "estimated_completion": "2024-01-15T10:30:00Z"
    } 