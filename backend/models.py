"""
SQLAlchemy models for JobFy.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

from .database import Base


class Job(Base):
    """Job offer model."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), default="N/A")
    salary = Column(String(100), default="N/A")
    tags = Column(Text, default="")
    apply_link = Column(String(500), nullable=False)
    source = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "salary": self.salary,
            "tags": self.tags,
            "apply_link": self.apply_link,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ScrapeLog(Base):
    """Log of scraping operations."""
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), default="")
    location = Column(String(255), default="")
    sites = Column(String(255), default="")
    jobs_found = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
