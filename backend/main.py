"""
FastAPI backend for JobFy - Job Scraper Dashboard.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db, init_db
from backend.models import Job, ScrapeLog
from config import SITES_CONFIG
from scrapers import (
    RemoteOKScraper,
    InfoJobsScraper,
    LinkedInScraper,
    IndeedScraper,
    TecnoempleoScraper,
)

app = FastAPI(
    title="JobFy API",
    description="API for job scraping and management",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scraper mapping
SCRAPERS = {
    "remoteok": RemoteOKScraper,
    "infojobs": InfoJobsScraper,
    "linkedin": LinkedInScraper,
    "indeed": IndeedScraper,
    "tecnoempleo": TecnoempleoScraper,
}


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


# ============== Jobs Endpoints ==============

@app.get("/api/jobs")
def get_jobs(
    db: Session = Depends(get_db),
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get all jobs with optional filtering."""
    query = db.query(Job)

    if source:
        query = query.filter(Job.source == source)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Job.job_title.ilike(search_term)) |
            (Job.company.ilike(search_term)) |
            (Job.tags.ilike(search_term))
        )

    total = query.count()
    jobs = query.order_by(desc(Job.created_at)).offset(offset).limit(limit).all()

    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted", "id": job_id}


@app.delete("/api/jobs")
def clear_jobs(db: Session = Depends(get_db)):
    """Delete all jobs."""
    count = db.query(Job).delete()
    db.commit()
    return {"message": f"Deleted {count} jobs"}


# ============== Stats Endpoints ==============

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get job statistics."""
    total_jobs = db.query(Job).count()

    # Jobs by source
    by_source = db.query(
        Job.source,
        func.count(Job.id).label("count")
    ).group_by(Job.source).all()

    # Jobs by company (top 10)
    by_company = db.query(
        Job.company,
        func.count(Job.id).label("count")
    ).group_by(Job.company).order_by(desc("count")).limit(10).all()

    # Jobs by location (top 10)
    by_location = db.query(
        Job.location,
        func.count(Job.id).label("count")
    ).group_by(Job.location).order_by(desc("count")).limit(10).all()

    # Extract and count tags
    all_tags = db.query(Job.tags).all()
    tag_counts = {}
    for (tags,) in all_tags:
        if tags:
            for tag in tags.split(","):
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "total_jobs": total_jobs,
        "by_source": [{"source": s, "count": c} for s, c in by_source],
        "by_company": [{"company": c, "count": n} for c, n in by_company],
        "by_location": [{"location": l, "count": n} for l, n in by_location],
        "top_tags": [{"tag": t, "count": c} for t, c in top_tags]
    }


# ============== Scraping Endpoints ==============

@app.get("/api/sites")
def get_sites():
    """Get available scraping sites."""
    return {
        "sites": [
            {
                "id": key,
                "name": config.name,
                "requires_auth": config.requires_auth
            }
            for key, config in SITES_CONFIG.items()
        ]
    }


def run_scrape(
    db: Session,
    log_id: int,
    sites: list[str],
    keyword: str,
    location: str
):
    """Background task to run scraping."""
    log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
    if not log:
        return

    log.status = "running"
    db.commit()

    total_jobs = 0
    errors = []

    try:
        for site_name in sites:
            if site_name not in SCRAPERS:
                errors.append(f"Unknown site: {site_name}")
                continue

            scraper_class = SCRAPERS[site_name]
            scraper = scraper_class()  # Scrapers initialize their own config

            try:
                jobs = scraper.scrape(keyword=keyword, location=location)

                for job in jobs:
                    # Check for duplicates by apply_link
                    existing = db.query(Job).filter(Job.apply_link == job.apply_link).first()
                    if not existing:
                        db_job = Job(
                            job_title=job.job_title,
                            company=job.company,
                            location=job.location,
                            salary=job.salary,
                            tags=job.tags,
                            apply_link=job.apply_link,
                            source=job.source
                        )
                        db.add(db_job)
                        total_jobs += 1

                db.commit()
            except Exception as e:
                errors.append(f"{site_name}: {str(e)}")
            finally:
                scraper.close()

        log.status = "completed"
        log.jobs_found = total_jobs
        log.completed_at = datetime.utcnow()
        if errors:
            log.error_message = "; ".join(errors)
        db.commit()

    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)
        log.completed_at = datetime.utcnow()
        db.commit()


@app.post("/api/scrape")
def start_scrape(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    sites: str = Query("remoteok", description="Comma-separated site names"),
    keyword: str = Query("", description="Search keyword"),
    location: str = Query("", description="Location filter")
):
    """Start a new scraping job."""
    site_list = [s.strip().lower() for s in sites.split(",") if s.strip()]

    if not site_list:
        raise HTTPException(status_code=400, detail="No sites specified")

    # Validate sites
    invalid_sites = [s for s in site_list if s not in SCRAPERS]
    if invalid_sites:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sites: {', '.join(invalid_sites)}"
        )

    # Create scrape log
    log = ScrapeLog(
        keyword=keyword,
        location=location,
        sites=",".join(site_list),
        status="pending"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Start background task
    background_tasks.add_task(run_scrape, db, log.id, site_list, keyword, location)

    return {
        "message": "Scraping started",
        "log_id": log.id,
        "sites": site_list,
        "keyword": keyword,
        "location": location
    }


@app.get("/api/scrape/logs")
def get_scrape_logs(db: Session = Depends(get_db), limit: int = 10):
    """Get recent scrape logs."""
    logs = db.query(ScrapeLog).order_by(desc(ScrapeLog.started_at)).limit(limit).all()
    return {
        "logs": [
            {
                "id": log.id,
                "keyword": log.keyword,
                "location": log.location,
                "sites": log.sites,
                "jobs_found": log.jobs_found,
                "status": log.status,
                "started_at": log.started_at.isoformat() if log.started_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }


@app.get("/api/scrape/logs/{log_id}")
def get_scrape_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific scrape log."""
    log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return {
        "id": log.id,
        "keyword": log.keyword,
        "location": log.location,
        "sites": log.sites,
        "jobs_found": log.jobs_found,
        "status": log.status,
        "started_at": log.started_at.isoformat() if log.started_at else None,
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "error_message": log.error_message
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
