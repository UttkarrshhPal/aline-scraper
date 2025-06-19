from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import re
from app.config import Config

class PdfProcessor:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.chunk_size = self.config.chunk_size
        self.chunk_overlap = self.config.chunk_overlap

    def extract_chapters(self, file_path: str, max_chapters: int = 8) -> List[str]:
        """Extract the first N chapters from a PDF file."""
        doc = fitz.Document(file_path)
        text = ""
        chapter_texts = []
        chapter_indices = []
        # Heuristic: find chapter starts by 'Chapter' or 'CHAPTER' in text
        for i in range(len(doc)):
            page = doc[i]
            page_text = page.get_text("text") # type: ignore
            if re.search(r'\bchapter\b', page_text, re.IGNORECASE):
                chapter_indices.append(i)
        chapter_indices = chapter_indices[:max_chapters] + [len(doc)]
        for i in range(len(chapter_indices)-1):
            start, end = chapter_indices[i], chapter_indices[i+1]
            chapter = ""
            for j in range(start, end):
                chapter += doc[j].get_text("text") # type: ignore
            chapter_texts.append(chapter)
        return chapter_texts

    def chunk_content(self, text: str) -> List[str]:
        """Chunk content into pieces with overlap, preserving paragraphs."""
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        chunks = []
        chunk = ""
        for para in paragraphs:
            if len(chunk) + len(para) < self.chunk_size:
                chunk += para + "\n"
            else:
                chunks.append(chunk.strip())
                # Overlap: take last chunk_overlap chars from previous chunk
                chunk = chunk[-self.chunk_overlap:] + para + "\n"
        if chunk:
            chunks.append(chunk.strip())
        return chunks

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        doc = fitz.Document(file_path)
        meta = doc.metadata
        if meta is None:
            meta = {}
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
        }

    def preserve_markdown_format(self, text: str) -> str:
        # Heuristic: preserve code blocks and lists
        text = re.sub(r'\n([ \t]*[-*+] )', '\n\1', text)  # lists
        text = re.sub(r'```', '', text)  # remove stray code fences
        # Add code fences for code blocks (simple heuristic)
        text = re.sub(r'\n([ \t]*def |[ \t]*class |[ \t]*for |[ \t]*if |[ \t]*while )', '\n```python\n\\1', text)
        text = re.sub(r'(\n\s*\n)', '\n```\n\\1', text)
        return text