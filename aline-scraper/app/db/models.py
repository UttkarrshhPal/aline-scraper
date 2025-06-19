from sqlalchemy import Column, String, Integer, Float, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class JobStatusEnum(enum.Enum):
    started = 'started'
    in_progress = 'in_progress'
    completed = 'completed'
    failed = 'failed'

class ScrapeJob(Base):
    __tablename__ = 'scrape_jobs'
    id = Column(String, primary_key=True)
    team_id = Column(String)
    user_id = Column(String)
    status = Column(Enum(JobStatusEnum), default=JobStatusEnum.started)
    progress = Column(Float, default=0.0)
    items_processed = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    errors = Column(Text)
    # Relationship to scraped items
    items = relationship('ScrapedItem', back_populates='job')

class ScrapedItem(Base):
    __tablename__ = 'scraped_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey('scrape_jobs.id'))
    title = Column(String)
    content = Column(Text)
    content_type = Column(String)
    source_url = Column(String)
    author = Column(String)
    user_id = Column(String)
    job = relationship('ScrapeJob', back_populates='items') 