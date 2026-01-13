"""Scraper para Tecnoempleo.com - Portal de empleo IT en Espana."""

import re
from typing import Optional
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from config import SITES_CONFIG
from .base import BaseScraper, JobOffer


class TecnoempleoScraper(BaseScraper):
    """
    Scraper para Tecnoempleo - especializado en ofertas de tecnologia.

    Tecnoempleo es un portal espanol enfocado en perfiles IT/Tech.
    No requiere autenticacion para busquedas.
    """

    SEARCH_URL = "https://www.tecnoempleo.com/busqueda-empleo.php"

    def __init__(self):
        super().__init__(SITES_CONFIG["tecnoempleo"])

    def _perform_login(self) -> bool:
        """Tecnoempleo no requiere login para busquedas."""
        return True

    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Construye URL de busqueda para Tecnoempleo.

        Args:
            keyword: Termino de busqueda (ej: "python", "java")
            location: Provincia (ej: "madrid", "barcelona")

        Returns:
            URL de busqueda
        """
        params = []

        if keyword:
            params.append(f"te={quote_plus(keyword)}")

        if location:
            params.append(f"pr={quote_plus(location)}")

        query = "&".join(params) if params else ""
        return f"{self.SEARCH_URL}?{query}" if query else self.SEARCH_URL

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """
        Parsea ofertas de Tecnoempleo.

        Args:
            html: HTML de la pagina de resultados

        Returns:
            Lista de JobOffer
        """
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Buscar todos los enlaces que parecen ser ofertas de trabajo
        # Tecnoempleo usa URLs como /desarrollador-python-madrid-123456
        all_links = soup.find_all("a", href=True)

        seen_urls = set()
        for link in all_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Filtrar enlaces que parecen ofertas de trabajo
            # Excluir navegacion, assets, paginas estaticas
            if not text or len(text) < 15 or len(text) > 80:
                continue
            if href in seen_urls:
                continue

            # Excluir URLs de navegacion y paginas estaticas
            exclude_patterns = [
                "assets", "graficos", "acceso", "registro", "newcand",
                "newemp", "accemp", "trabajo/", "empleo-publico",
                "tecnocalculadora", "servicios", ".php", ".css", ".js",
                "pagina=", "second-window", "aws-trabajo", "ofertas-trabajo/"
            ]
            if any(x in href.lower() for x in exclude_patterns):
                continue

            # Excluir URLs que terminan en "-trabajo" (paginas de empresa)
            if href.rstrip("/").endswith("-trabajo"):
                continue

            # Normalizar href (puede ser absoluto o relativo)
            if href.startswith("https://www.tecnoempleo.com/"):
                href_path = href.replace("https://www.tecnoempleo.com", "")
            elif href.startswith("/"):
                href_path = href
            else:
                continue

            # Las ofertas tienen formato: /titulo-puesto-ubicacion-id
            if "-" in href_path and len(href_path) > 15:
                # Extraer datos del enlace
                job = self._extract_job_from_link(link, href)
                if job:
                    seen_urls.add(href)
                    jobs.append(job)

        return jobs[:30]  # Limitar resultados

    def _extract_job_from_link(self, link_elem, href: str) -> Optional[JobOffer]:
        """Extrae datos de un enlace de oferta."""
        try:
            job_title = link_elem.get_text(strip=True)

            if not job_title or len(job_title) < 5:
                return None

            # Construir URL completa
            apply_link = urljoin(self.config.base_url, href)

            # Intentar extraer empresa del contexto (elemento hermano o padre)
            company = "N/A"
            parent = link_elem.parent
            if parent:
                # Buscar enlace de empresa cercano
                company_link = parent.find("a", href=lambda x: x and "-trabajo" in x if x else False)
                if company_link:
                    company = company_link.get_text(strip=True)

            # Intentar extraer ubicacion del titulo
            location = "Espana"
            location_patterns = [
                "madrid", "barcelona", "valencia", "sevilla", "bilbao",
                "malaga", "zaragoza", "remote", "remoto", "teletrabajo"
            ]
            title_lower = job_title.lower()
            for loc in location_patterns:
                if loc in title_lower:
                    location = loc.capitalize()
                    break

            return JobOffer(
                job_title=job_title,
                company=company,
                tags="IT/Tech",
                apply_link=apply_link,
                location=location,
                salary="N/A"
            )

        except Exception:
            return None

    def _extract_job(self, card: BeautifulSoup) -> Optional[JobOffer]:
        """Metodo legacy - mantenido por compatibilidad."""
        return None
