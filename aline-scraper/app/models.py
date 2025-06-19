from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    author: Optional[str] = None
    max_pages: Optional[int] = None
    chunk_size: Optional[int] = 1000

class Source(BaseModel):
    type: Literal['blog', 'pdf', 'guide_collection']
    url: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Metadata] = None

class ScrapingRequest(BaseModel):
    team_id: str
    user_id: str
    sources: List[Source]

class ScrapedItem(BaseModel):
    title: str
    content: str
    content_type: Literal[
        'blog', 'podcast_transcript', 'call_transcript', 'linkedin_post',
        'reddit_comment', 'book', 'other'
    ]
    source_url: Optional[str] = None
    author: Optional[str] = ''
    user_id: Optional[str] = ''

class ScrapeResponse(BaseModel):
    team_id: str
    items: List[ScrapedItem] 