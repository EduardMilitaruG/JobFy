# JobFy - Multi-Site Job Scraper

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-43B02A?style=for-the-badge)
![Requests](https://img.shields.io/badge/Requests-HTTP-2CA5E0?style=for-the-badge)

A Python-based web scraping tool that extracts job listings from multiple employment portals and exports them to CSV format. Built with extensibility in mind using the Template Method design pattern.

## Supported Sites

| Site | Login Required | Status | Description |
|------|----------------|--------|-------------|
| **RemoteOK** | No | Working | Global remote jobs (uses JSON API) |
| **Tecnoempleo** | No | Working | IT jobs in Spain |
| InfoJobs | Yes | Optional | Leading job portal in Spain |
| LinkedIn | Yes | Optional | Global professional network |
| Indeed | No | Blocked | Anti-bot protection active |

> **Recommended:** Start with RemoteOK and Tecnoempleo - no additional configuration required.

## Key Features

- **Multi-platform scraping** - Query multiple job sites in a single command
- **Flexible CLI interface** - Filter by keyword, location, and specific sites
- **Extensible architecture** - Template Method pattern for easy addition of new scrapers
- **CSV export** - Structured output for further analysis
- **Secure credential management** - Environment variables for sensitive data

## Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/JobFy.git
cd JobFy
python -m venv venv
source venv/bin/activate  # Linux/Mac (or venv\Scripts\activate on Windows)
pip install -r requirements.txt

# Run a search
python jobfy_scraper.py -s remoteok,tecnoempleo -k "python"
```

## Tech Stack

- **Python 3.10+** - Core language
- **requests** - HTTP client
- **BeautifulSoup4** - HTML parsing
- **python-dotenv** - Environment variable management
- **argparse** - CLI interface

## Usage Examples

```bash
# Search "python" on RemoteOK and Tecnoempleo
python jobfy_scraper.py -s remoteok,tecnoempleo -k "python"

# Search with location filter
python jobfy_scraper.py -s tecnoempleo -k "java" -l "Madrid"

# Remote jobs only (RemoteOK default)
python jobfy_scraper.py -k "react"

# View available sites
python jobfy_scraper.py --list-sites

# Check configuration status
python jobfy_scraper.py --status
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--keyword` | `-k` | Search term |
| `--location` | `-l` | Location/city filter |
| `--sites` | `-s` | Comma-separated site list |
| `--all` | `-a` | Use all available sites |
| `--output` | `-o` | Output CSV filename |
| `--list-sites` | | List available sites |
| `--status` | | Show configuration status |

## Sample Output

```
[CONFIG] Selected sites: remoteok, tecnoempleo
[CONFIG] Search: 'python'

============================================================
STARTING SCRAPE
============================================================

[RemoteOK] Starting scrape...
  [INFO] URL: https://remoteok.com/api
  [OK] Found 3 listings

[Tecnoempleo] Starting scrape...
  [INFO] URL: https://www.tecnoempleo.com/busqueda-empleo.php?te=python
  [OK] Found 30 listings

============================================================
SEARCH SUMMARY
============================================================

Total listings found: 33

Breakdown by site:
  - RemoteOK: 3 listings
  - Tecnoempleo: 30 listings

[OK] File saved: output/jobs_python_20240115_143052.csv
```

## Project Structure

```
JobFy/
├── jobfy_scraper.py      # Main CLI script
├── config.py             # Configuration and credentials
├── requirements.txt      # Dependencies
├── .env.example          # Template (no real data)
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   ├── remoteok.py       # RemoteOK JSON API
│   ├── tecnoempleo.py    # Tecnoempleo scraper
│   ├── infojobs.py       # InfoJobs (requires login)
│   ├── linkedin.py       # LinkedIn (requires login)
│   └── indeed.py         # Indeed (blocked)
└── output/
    └── *.csv             # Generated files
```

## Architecture

The project implements the **Template Method** design pattern with an abstract base class:

```python
class BaseScraper(ABC):
    @abstractmethod
    def _perform_login(self) -> bool: ...

    @abstractmethod
    def get_search_url(self, keyword, location) -> str: ...

    @abstractmethod
    def parse_job_listings(self, html) -> list[JobOffer]: ...

    def scrape(self, keyword, location) -> list[JobOffer]:
        # Common logic: login -> fetch -> parse
```

This architecture enables easy addition of new job sites by inheriting from `BaseScraper`.

## Adding New Sites

1. Create `scrapers/new_site.py`
2. Inherit from `BaseScraper`
3. Implement the abstract methods
4. Register in `config.py` and `jobfy_scraper.py`

```python
from .base import BaseScraper, JobOffer

class NewSiteScraper(BaseScraper):
    def _perform_login(self) -> bool:
        return True  # or implement login

    def get_search_url(self, keyword: str, location: str) -> str:
        return f"https://newsite.com/jobs?q={keyword}"

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        # Implement parsing with BeautifulSoup
        ...
```

## Optional Configuration (InfoJobs/LinkedIn)

> **Warning:** InfoJobs and LinkedIn may block accounts for automated use. Use at your own risk.

```bash
# Create credentials file
cp .env.example .env

# Edit .env with your credentials
INFOJOBS_USERNAME=your_email@example.com
INFOJOBS_PASSWORD=your_password
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

## Known Limitations

- **Indeed:** Currently blocked by anti-bot protection (403 error)
- **InfoJobs/LinkedIn:** May display captchas or block accounts
- **HTML Structure:** Sites frequently change their DOM selectors
- **Rate Limiting:** Excessive requests may result in temporary blocks

## Skills Demonstrated

- Web scraping with BeautifulSoup and requests
- Object-oriented design patterns (Template Method)
- CLI development with argparse
- Environment variable management
- API integration (RemoteOK JSON API)
- Error handling and graceful degradation
- Code organization and project structure

## Author

**Eduard Militaru**
- GitHub: [@EduardMilitaruG](https://github.com/EduardMilitaruG)
- LinkedIn: [Eduard Militaru](https://linkedin.com/in/eduardmilitaru)

## License

MIT License - Free for personal and educational use.

---

*Built as a portfolio project demonstrating Python and web scraping skills*
