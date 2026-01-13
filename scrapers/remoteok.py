"""Scraper para RemoteOK.com - Empleos remotos (usa API JSON)."""

import json
from typing import Optional
from urllib.parse import quote_plus

import requests

from config import SITES_CONFIG
from .base import BaseScraper, JobOffer


class RemoteOKScraper(BaseScraper):
    """
    Scraper para RemoteOK - sitio de trabajos remotos.

    Usa la API publica JSON de RemoteOK para mayor confiabilidad.
    """

    API_URL = "https://remoteok.com/api"

    def __init__(self):
        super().__init__(SITES_CONFIG["remoteok"])
        # Crear nueva sesion con headers especificos para la API
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _perform_login(self) -> bool:
        """RemoteOK no requiere login."""
        return True

    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Retorna la URL de la API.

        Args:
            keyword: Termino de busqueda (filtrado localmente)
            location: No aplica para RemoteOK

        Returns:
            URL de la API
        """
        return self.API_URL

    def scrape(self, keyword: str = "", location: str = "") -> list[JobOffer]:
        """
        Obtiene ofertas desde la API de RemoteOK.

        Args:
            keyword: Termino de busqueda para filtrar
            location: No aplica

        Returns:
            Lista de ofertas
        """
        print(f"\n[{self.name}] Iniciando scraping...")
        print(f"  [INFO] URL: {self.API_URL}")

        try:
            response = self.session.get(self.API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"  [ERROR] Error obteniendo API: {e}")
            return []

        jobs = self._parse_api_response(data, keyword)

        for job in jobs:
            job.source = self.name

        print(f"  [OK] Encontradas {len(jobs)} ofertas")
        return jobs

    def _parse_api_response(self, data: list, keyword: str = "") -> list[JobOffer]:
        """
        Parsea la respuesta JSON de la API.

        Args:
            data: Lista de ofertas desde la API
            keyword: Filtro opcional

        Returns:
            Lista de JobOffer
        """
        jobs = []
        keyword_lower = keyword.lower() if keyword else ""

        for item in data:
            # El primer elemento es metadata, saltarlo
            if "legal" in item:
                continue

            job = self._extract_job(item)
            if job:
                # Filtrar por keyword si se especifico
                if keyword_lower:
                    searchable = f"{job.job_title} {job.company} {job.tags}".lower()
                    if keyword_lower not in searchable:
                        continue
                jobs.append(job)

        return jobs[:50]  # Limitar a 50 resultados

    def _extract_job(self, item: dict) -> Optional[JobOffer]:
        """Extrae datos de un item de la API."""
        try:
            job_title = item.get("position", "")
            if not job_title:
                return None

            company = item.get("company", "N/A")

            # Tags
            tags_list = item.get("tags", [])
            tags = ", ".join(tags_list) if tags_list else "N/A"

            # URL
            slug = item.get("slug", "")
            apply_link = f"{self.config.base_url}/{slug}" if slug else item.get("url", "N/A")

            # Salario
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            if salary_min and salary_max:
                salary = f"${salary_min:,} - ${salary_max:,}"
            elif salary_min:
                salary = f"${salary_min:,}+"
            else:
                salary = "N/A"

            # Ubicacion
            location = item.get("location", "Remote") or "Remote"

            return JobOffer(
                job_title=job_title,
                company=company,
                tags=tags,
                apply_link=apply_link,
                location=location,
                salary=salary
            )

        except Exception:
            return None

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """No usado - mantenido por compatibilidad con clase base."""
        return []
