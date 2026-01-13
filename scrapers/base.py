"""
Clase base abstracta para todos los scrapers.
Define la interfaz comun que deben implementar todos los scrapers de sitios.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import SiteConfig, HEADERS, REQUEST_TIMEOUT


@dataclass
class JobOffer:
    """Representa una oferta de trabajo extraida."""
    job_title: str
    company: str
    tags: str
    apply_link: str
    location: str = "N/A"
    salary: str = "N/A"
    source: str = "N/A"

    def to_dict(self) -> dict:
        """Convierte la oferta a diccionario."""
        return asdict(self)


class BaseScraper(ABC):
    """
    Clase base abstracta para scrapers de sitios de empleo.

    Cada sitio debe implementar sus propios metodos de parsing
    heredando de esta clase.
    """

    def __init__(self, config: SiteConfig):
        """
        Inicializa el scraper con la configuracion del sitio.

        Args:
            config: Configuracion del sitio (URL, credenciales, etc)
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._authenticated = False

    @property
    def name(self) -> str:
        """Nombre del sitio."""
        return self.config.name

    @property
    def requires_auth(self) -> bool:
        """Indica si el sitio requiere autenticacion."""
        return self.config.requires_auth

    @property
    def is_authenticated(self) -> bool:
        """Indica si ya se ha autenticado."""
        return self._authenticated

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Realiza una peticion HTTP y retorna el contenido HTML.

        Args:
            url: URL a consultar

        Returns:
            Contenido HTML de la pagina o None si hay error
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            print(f"  [ERROR] Timeout al conectar con {url}")
        except requests.exceptions.HTTPError as e:
            print(f"  [ERROR] HTTP {e.response.status_code}: {url}")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Error de conexion: {e}")
        return None

    def login(self) -> bool:
        """
        Realiza el proceso de autenticacion en el sitio.

        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        if not self.requires_auth:
            return True

        if not self.config.credentials:
            print(f"  [ERROR] {self.name} requiere credenciales.")
            print(f"  Configura {self.name.upper()}_USERNAME y {self.name.upper()}_PASSWORD en .env")
            return False

        return self._perform_login()

    @abstractmethod
    def _perform_login(self) -> bool:
        """
        Implementacion especifica del login para cada sitio.
        Debe ser implementado por cada scraper.

        Returns:
            True si el login fue exitoso
        """
        pass

    @abstractmethod
    def get_search_url(self, keyword: str = "", location: str = "") -> str:
        """
        Construye la URL de busqueda para el sitio.

        Args:
            keyword: Termino de busqueda (ej: "python developer")
            location: Ubicacion (ej: "Madrid")

        Returns:
            URL completa de busqueda
        """
        pass

    @abstractmethod
    def parse_job_listings(self, html: str) -> list[JobOffer]:
        """
        Parsea el HTML y extrae las ofertas de trabajo.

        Args:
            html: Contenido HTML de la pagina de resultados

        Returns:
            Lista de ofertas de trabajo encontradas
        """
        pass

    def scrape(self, keyword: str = "", location: str = "") -> list[JobOffer]:
        """
        Ejecuta el proceso completo de scraping.

        Args:
            keyword: Termino de busqueda
            location: Ubicacion

        Returns:
            Lista de ofertas extraidas
        """
        print(f"\n[{self.name}] Iniciando scraping...")

        # Autenticacion si es necesaria
        if self.requires_auth:
            if not self.login():
                print(f"  [ERROR] No se pudo autenticar en {self.name}")
                return []
            print(f"  [OK] Autenticacion exitosa")

        # Obtener URL de busqueda
        search_url = self.get_search_url(keyword, location)
        print(f"  [INFO] URL: {search_url}")

        # Descargar pagina
        html = self.fetch_page(search_url)
        if not html:
            print(f"  [ERROR] No se pudo descargar la pagina")
            return []

        # Parsear ofertas
        jobs = self.parse_job_listings(html)

        # Agregar fuente a cada oferta
        for job in jobs:
            job.source = self.name

        print(f"  [OK] Encontradas {len(jobs)} ofertas")
        return jobs

    def close(self) -> None:
        """Cierra la sesion HTTP."""
        self.session.close()
