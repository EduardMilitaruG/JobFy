"""Scraper para InfoJobs.net - Portal de empleo en Espana."""

from typing import Optional
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from config import SITES_CONFIG
from .base import BaseScraper, JobOffer


class InfoJobsScraper(BaseScraper):
    """
    Scraper para InfoJobs - principal portal de empleo en Espana.

    NOTA: InfoJobs tiene protecciones anti-scraping. El login via web
    puede requerir captchas. Para uso profesional, considera usar su API oficial.
    """

    LOGIN_URL = "https://www.infojobs.net/candidate/access/login.xhtml"
    SEARCH_URL = "https://www.infojobs.net/jobsearch/search-results/list.xhtml"

    def __init__(self):
        super().__init__(SITES_CONFIG["infojobs"])

    def _perform_login(self) -> bool:
        """
        Intenta autenticarse en InfoJobs.

        ADVERTENCIA: InfoJobs puede mostrar captchas o bloquear
        intentos de login automatizado.

        Returns:
            True si el login fue exitoso
        """
        if not self.config.credentials:
            return False

        try:
            # Obtener pagina de login para cookies iniciales
            login_page = self.fetch_page(self.LOGIN_URL)
            if not login_page:
                return False

            # Preparar datos de login
            login_data = {
                "j_username": self.config.credentials.username,
                "j_password": self.config.credentials.password,
            }

            # Intentar login
            response = self.session.post(
                self.LOGIN_URL,
                data=login_data,
                allow_redirects=True
            )

            # Verificar si el login fue exitoso
            if "logout" in response.text.lower() or "mi-cv" in response.url:
                self._authenticated = True
                return True

            print("  [WARNING] Login puede haber fallado - posible captcha")
            # Continuamos de todas formas, algunas busquedas funcionan sin login
            return True

        except Exception as e:
            print(f"  [ERROR] Error en login: {e}")
            return False

    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Construye URL de busqueda para InfoJobs.

        Args:
            keyword: Termino de busqueda (ej: "python developer")
            location: Ubicacion (ej: "Madrid", "Barcelona")

        Returns:
            URL de busqueda
        """
        params = []

        if keyword:
            params.append(f"q={quote_plus(keyword)}")

        if location:
            params.append(f"provinceIds={quote_plus(location)}")

        query = "&".join(params) if params else ""
        return f"{self.SEARCH_URL}?{query}" if query else self.SEARCH_URL

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """
        Parsea ofertas de InfoJobs.

        Args:
            html: HTML de la pagina de resultados

        Returns:
            Lista de JobOffer
        """
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # InfoJobs usa diferentes estructuras, intentamos varias
        job_cards = soup.find_all("div", class_="ij-OfferCardContent")

        if not job_cards:
            # Estructura alternativa
            job_cards = soup.find_all("li", class_="ij-OfferCard")

        if not job_cards:
            # Otra estructura posible
            job_cards = soup.select("[data-testid='offer-card']")

        for card in job_cards:
            job = self._extract_job(card)
            if job:
                jobs.append(job)

        return jobs

    def _extract_job(self, card: BeautifulSoup) -> Optional[JobOffer]:
        """Extrae datos de una tarjeta de oferta."""
        try:
            # Titulo - varios selectores posibles
            title_elem = (
                card.find("a", class_="ij-OfferCardContent-description-title-link") or
                card.find("h2", class_="ij-OfferCardContent-description-title") or
                card.select_one("[data-testid='offer-title']") or
                card.find("a", {"data-test": "offer-title"})
            )

            job_title = title_elem.get_text(strip=True) if title_elem else None
            if not job_title:
                return None

            # Link de la oferta
            apply_link = "N/A"
            if title_elem and title_elem.name == "a":
                href = title_elem.get("href", "")
                apply_link = urljoin(self.config.base_url, href) if href else "N/A"

            # Empresa
            company_elem = (
                card.find("a", class_="ij-OfferCardContent-description-subtitle-link") or
                card.select_one("[data-testid='offer-company']") or
                card.find("span", class_="ij-OfferCardContent-description-subtitle")
            )
            company = company_elem.get_text(strip=True) if company_elem else "N/A"

            # Ubicacion
            location_elem = (
                card.find("span", class_="ij-OfferCardContent-description-list-item-truncate") or
                card.select_one("[data-testid='offer-location']")
            )
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # Salario
            salary_elem = card.find("span", class_="ij-OfferCardContent-description-salary")
            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"

            # Tags (requisitos, tecnologias)
            tag_elements = card.find_all("span", class_="ij-OfferCardContent-description-tag")
            tags = ", ".join([t.get_text(strip=True) for t in tag_elements]) or "N/A"

            return JobOffer(
                job_title=job_title,
                company=company,
                tags=tags,
                apply_link=apply_link,
                location=location,
                salary=salary
            )

        except Exception as e:
            print(f"  [WARNING] Error parseando oferta InfoJobs: {e}")
            return None
