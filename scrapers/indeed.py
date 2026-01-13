"""Scraper para Indeed.com - Portal global de empleo."""

from typing import Optional
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from config import SITES_CONFIG
from .base import BaseScraper, JobOffer


class IndeedScraper(BaseScraper):
    """
    Scraper para Indeed - uno de los mayores portales de empleo.

    Indeed permite busquedas sin autenticacion, pero tiene
    protecciones anti-bot que pueden bloquear requests automatizados.
    """

    def __init__(self, country: str = "es"):
        """
        Inicializa el scraper de Indeed.

        Args:
            country: Codigo de pais (es, com, co.uk, etc.)
        """
        super().__init__(SITES_CONFIG["indeed"])
        self.country = country
        self._update_base_url()

    def _update_base_url(self) -> None:
        """Actualiza la URL base segun el pais."""
        if self.country == "es":
            self.config.base_url = "https://es.indeed.com"
        elif self.country == "mx":
            self.config.base_url = "https://mx.indeed.com"
        elif self.country == "ar":
            self.config.base_url = "https://ar.indeed.com"
        # Default: indeed.com (USA)

    def _perform_login(self) -> bool:
        """Indeed no requiere login para busquedas basicas."""
        return True

    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Construye URL de busqueda para Indeed.

        Args:
            keyword: Termino de busqueda (ej: "python developer")
            location: Ubicacion (ej: "Madrid")

        Returns:
            URL de busqueda
        """
        params = []

        if keyword:
            params.append(f"q={quote_plus(keyword)}")

        if location:
            params.append(f"l={quote_plus(location)}")

        # Ordenar por fecha
        params.append("sort=date")

        query = "&".join(params)
        return f"{self.config.base_url}/jobs?{query}"

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """
        Parsea ofertas de Indeed.

        Args:
            html: HTML de la pagina de resultados

        Returns:
            Lista de JobOffer
        """
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Indeed usa varias estructuras de tarjetas
        job_cards = soup.find_all("div", class_="job_seen_beacon")

        if not job_cards:
            job_cards = soup.find_all("div", class_="jobsearch-SerpJobCard")

        if not job_cards:
            job_cards = soup.select("[data-jk]")  # data-jk es el ID del trabajo

        if not job_cards:
            # Estructura mas reciente
            job_cards = soup.find_all("td", class_="resultContent")

        for card in job_cards:
            job = self._extract_job(card)
            if job:
                jobs.append(job)

        return jobs

    def _extract_job(self, card: BeautifulSoup) -> Optional[JobOffer]:
        """Extrae datos de una tarjeta de Indeed."""
        try:
            # Titulo
            title_elem = (
                card.find("h2", class_="jobTitle") or
                card.find("a", class_="jobtitle") or
                card.select_one("[data-testid='jobTitle']") or
                card.find("span", {"title": True})
            )

            job_title = None
            if title_elem:
                # El titulo puede estar en un span interno
                span = title_elem.find("span")
                job_title = span.get_text(strip=True) if span else title_elem.get_text(strip=True)

            if not job_title:
                return None

            # Link de la oferta
            apply_link = "N/A"
            link_elem = card.find("a", class_="jcs-JobTitle") or card.find("a", href=True)
            if link_elem:
                href = link_elem.get("href", "")
                if href:
                    if href.startswith("/"):
                        apply_link = urljoin(self.config.base_url, href)
                    elif href.startswith("http"):
                        apply_link = href

            # Empresa
            company_elem = (
                card.find("span", class_="companyName") or
                card.find("span", {"data-testid": "company-name"}) or
                card.find("a", class_="companyName")
            )
            company = company_elem.get_text(strip=True) if company_elem else "N/A"

            # Ubicacion
            location_elem = (
                card.find("div", class_="companyLocation") or
                card.find("span", class_="location") or
                card.find("div", {"data-testid": "text-location"})
            )
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # Salario (si esta disponible)
            salary_elem = (
                card.find("div", class_="salary-snippet-container") or
                card.find("span", class_="salaryText") or
                card.find("div", {"data-testid": "attribute_snippet_testid"})
            )
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"

            # Tags/Atributos del trabajo
            tags_list = []
            attribute_elems = card.find_all("div", class_="attribute_snippet")
            for attr in attribute_elems:
                tags_list.append(attr.get_text(strip=True))

            tags = ", ".join(tags_list) if tags_list else "N/A"

            return JobOffer(
                job_title=job_title,
                company=company,
                tags=tags,
                apply_link=apply_link,
                location=location,
                salary=salary
            )

        except Exception as e:
            print(f"  [WARNING] Error parseando oferta Indeed: {e}")
            return None
