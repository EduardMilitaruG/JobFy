"""Scraper para LinkedIn Jobs."""

from typing import Optional
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from config import SITES_CONFIG
from .base import BaseScraper, JobOffer


class LinkedInScraper(BaseScraper):
    """
    Scraper para LinkedIn Jobs.

    ADVERTENCIA IMPORTANTE:
    LinkedIn tiene politicas muy estrictas contra el scraping automatizado.
    El uso de este scraper puede resultar en:
    - Bloqueo temporal o permanente de tu cuenta
    - Restricciones de IP
    - Posibles acciones legales

    RECOMENDACION: Usar la API oficial de LinkedIn o buscar ofertas manualmente.
    Este codigo es solo con fines educativos.
    """

    LOGIN_URL = "https://www.linkedin.com/login"
    SESSION_URL = "https://www.linkedin.com/uas/login-submit"
    JOBS_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self):
        super().__init__(SITES_CONFIG["linkedin"])
        # Headers adicionales para LinkedIn
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.linkedin.com/",
        })

    def _perform_login(self) -> bool:
        """
        Intenta autenticarse en LinkedIn.

        NOTA: LinkedIn tiene multiples capas de proteccion:
        - CSRF tokens
        - Captchas
        - Verificacion de dispositivo
        - Rate limiting agresivo

        Returns:
            True si el login fue exitoso
        """
        if not self.config.credentials:
            return False

        try:
            # Obtener pagina de login para CSRF token
            login_page = self.fetch_page(self.LOGIN_URL)
            if not login_page:
                print("  [ERROR] No se pudo acceder a la pagina de login")
                return False

            soup = BeautifulSoup(login_page, "html.parser")

            # Buscar CSRF token
            csrf_token = None
            csrf_input = soup.find("input", {"name": "loginCsrfParam"})
            if csrf_input:
                csrf_token = csrf_input.get("value")

            if not csrf_token:
                print("  [WARNING] No se encontro CSRF token")
                # Intentamos sin el token
                csrf_token = ""

            # Preparar datos de login
            login_data = {
                "session_key": self.config.credentials.username,
                "session_password": self.config.credentials.password,
                "loginCsrfParam": csrf_token,
            }

            # Intentar login
            response = self.session.post(
                self.SESSION_URL,
                data=login_data,
                allow_redirects=True
            )

            # Verificar exito
            if "feed" in response.url or "mynetwork" in response.url:
                self._authenticated = True
                print("  [OK] Login exitoso en LinkedIn")
                return True

            # Verificar si hay challenge de seguridad
            if "challenge" in response.url or "checkpoint" in response.url:
                print("  [ERROR] LinkedIn requiere verificacion adicional")
                print("  Por favor, inicia sesion manualmente y completa la verificacion")
                return False

            print("  [WARNING] No se pudo confirmar el login")
            return False

        except Exception as e:
            print(f"  [ERROR] Error en login de LinkedIn: {e}")
            return False

    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Construye URL de busqueda para LinkedIn Jobs.

        Args:
            keyword: Termino de busqueda
            location: Ubicacion

        Returns:
            URL de busqueda
        """
        params = []

        if keyword:
            params.append(f"keywords={quote_plus(keyword)}")

        if location:
            params.append(f"location={quote_plus(location)}")

        # Parametros adicionales utiles
        params.append("f_TPR=r604800")  # Ultimos 7 dias
        params.append("sortBy=R")  # Ordenar por relevancia

        query = "&".join(params)
        return f"{self.JOBS_URL}?{query}"

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """
        Parsea ofertas de LinkedIn Jobs.

        Args:
            html: HTML de la pagina de resultados

        Returns:
            Lista de JobOffer
        """
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # LinkedIn cambia frecuentemente sus clases CSS
        # Intentamos varios selectores

        # Selector para vista de busqueda
        job_cards = soup.find_all("div", class_="base-card")

        if not job_cards:
            job_cards = soup.find_all("li", class_="jobs-search-results__list-item")

        if not job_cards:
            job_cards = soup.select("[data-job-id]")

        for card in job_cards:
            job = self._extract_job(card)
            if job:
                jobs.append(job)

        if not jobs:
            print("  [WARNING] No se encontraron ofertas - LinkedIn puede estar bloqueando")

        return jobs

    def _extract_job(self, card: BeautifulSoup) -> Optional[JobOffer]:
        """Extrae datos de una tarjeta de trabajo de LinkedIn."""
        try:
            # Titulo
            title_elem = (
                card.find("h3", class_="base-search-card__title") or
                card.find("a", class_="job-card-list__title") or
                card.select_one("[class*='job-title']")
            )
            job_title = title_elem.get_text(strip=True) if title_elem else None

            if not job_title:
                return None

            # Empresa
            company_elem = (
                card.find("h4", class_="base-search-card__subtitle") or
                card.find("a", class_="job-card-container__company-name") or
                card.select_one("[class*='company-name']")
            )
            company = company_elem.get_text(strip=True) if company_elem else "N/A"

            # Ubicacion
            location_elem = (
                card.find("span", class_="job-search-card__location") or
                card.find("li", class_="job-card-container__metadata-item") or
                card.select_one("[class*='location']")
            )
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # Link
            link_elem = card.find("a", class_="base-card__full-link")
            if not link_elem:
                link_elem = card.find("a", href=True)

            apply_link = "N/A"
            if link_elem:
                href = link_elem.get("href", "")
                if href.startswith("http"):
                    apply_link = href.split("?")[0]  # Limpiar parametros de tracking
                else:
                    apply_link = urljoin(self.config.base_url, href)

            return JobOffer(
                job_title=job_title,
                company=company,
                tags="N/A",  # LinkedIn no muestra tags directamente en la lista
                apply_link=apply_link,
                location=location,
                salary="N/A"
            )

        except Exception as e:
            print(f"  [WARNING] Error parseando oferta LinkedIn: {e}")
            return None
