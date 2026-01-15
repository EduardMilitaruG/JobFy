# JobFy - Multi-Site Job Scraper Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

A full-stack web application that scrapes job listings from multiple employment portals, stores them in a database, and displays them in an interactive dashboard with analytics.

## Features

### Backend (Python/FastAPI)
- **Multi-platform scraping** - Query multiple job sites in a single request
- **RESTful API** - Full CRUD operations for job listings
- **SQLite database** - Persistent storage with SQLAlchemy ORM
- **Background tasks** - Async scraping with status tracking
- **Statistics API** - Aggregated data for charts and analytics

### Frontend (React)
- **Job table** - Searchable, filterable list with pagination
- **Statistics dashboard** - Interactive charts with Recharts
- **Scrape panel** - Trigger new scrapes from the UI
- **Dark theme** - Modern, responsive design
- **Real-time filtering** - Filter by source, keyword, location

## Supported Sites

| Site | Login Required | Status |
|------|----------------|--------|
| **RemoteOK** | No | ✅ Working |
| **Tecnoempleo** | No | ✅ Working |
| InfoJobs | Yes | ⚠️ Optional |
| LinkedIn | Yes | ⚠️ Optional |
| Indeed | No | ❌ Blocked |

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy + SQLite
- BeautifulSoup4
- Requests

**Frontend:**
- React 18
- Vite
- Recharts
- Lucide Icons

## Quick Start

### 1. Clone and Setup Backend

```bash
git clone https://github.com/EduardMilitaruG/JobFy.git
cd JobFy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
cd backend
python main.py
# API running at http://localhost:8000
```

### 3. Setup and Start Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

## Project Structure

```
JobFy/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── database.py       # SQLAlchemy setup
│   └── models.py         # Database models
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main application
│   │   ├── components/
│   │   │   ├── JobTable.jsx      # Job listings table
│   │   │   ├── StatsCharts.jsx   # Analytics charts
│   │   │   └── ScrapePanel.jsx   # Scrape controls
│   │   └── App.css       # Styles
│   └── package.json
├── scrapers/
│   ├── base.py           # Abstract base scraper
│   ├── remoteok.py       # RemoteOK scraper
│   ├── tecnoempleo.py    # Tecnoempleo scraper
│   └── ...
├── config.py             # Site configurations
├── jobfy_scraper.py      # CLI script (legacy)
└── requirements.txt
```

## API Endpoints

### Jobs
- `GET /api/jobs` - List jobs (with search, filter, pagination)
- `GET /api/jobs/{id}` - Get single job
- `DELETE /api/jobs/{id}` - Delete job
- `DELETE /api/jobs` - Clear all jobs

### Statistics
- `GET /api/stats` - Get aggregated statistics

### Scraping
- `GET /api/sites` - List available sites
- `POST /api/scrape` - Start new scrape
- `GET /api/scrape/logs` - Get scrape history

## CLI Usage (Legacy)

The original CLI is still available:

```bash
# Search "python" on RemoteOK and Tecnoempleo
python jobfy_scraper.py -s remoteok,tecnoempleo -k "python"

# Search with location filter
python jobfy_scraper.py -s tecnoempleo -k "java" -l "Madrid"

# View available sites
python jobfy_scraper.py --list-sites
```

## Screenshots

### Jobs Dashboard
- Search and filter job listings
- Sort by date, company, or source
- Quick apply links

### Statistics
- Jobs by source (pie chart)
- Top companies hiring
- Most requested skills
- Job locations

### Scrape Panel
- Select sites to scrape
- Set keyword and location filters
- View scrape history and status

## Skills Demonstrated

- **Full-stack development** - Python backend + React frontend
- **REST API design** - FastAPI with proper routing and validation
- **Database design** - SQLAlchemy ORM with SQLite
- **Web scraping** - BeautifulSoup, requests, anti-bot handling
- **Data visualization** - Recharts for interactive analytics
- **Modern React** - Hooks, functional components, state management
- **Responsive design** - CSS Grid, Flexbox, mobile-first approach

## Author

**Eduard Militaru**
- GitHub: [@EduardMilitaruG](https://github.com/EduardMilitaruG)
- LinkedIn: [Eduard Militaru](https://linkedin.com/in/eduardmilitaru)

## License

MIT License - Free for personal and educational use.

---

*Built as a portfolio project demonstrating Python, web scraping, and full-stack development skills*
