"""
Configuracion centralizada y manejo de credenciales.
Las credenciales se cargan desde variables de entorno o archivo .env
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Cargar variables desde .env si existe
load_dotenv()


@dataclass
class Credentials:
    """Credenciales para un sitio especifico."""
    username: str
    password: str


@dataclass
class SiteConfig:
    """Configuracion de un sitio de empleo."""
    name: str
    base_url: str
    requires_auth: bool
    credentials: Optional[Credentials] = None


def get_credentials(site: str) -> Optional[Credentials]:
    """
    Obtiene las credenciales para un sitio desde variables de entorno.

    Variables esperadas:
        {SITE}_USERNAME
        {SITE}_PASSWORD

    Args:
        site: Nombre del sitio (ej: "INFOJOBS", "LINKEDIN")

    Returns:
        Credentials si existen, None si no estan configuradas
    """
    username = os.getenv(f"{site.upper()}_USERNAME")
    password = os.getenv(f"{site.upper()}_PASSWORD")

    if username and password:
        return Credentials(username=username, password=password)
    return None


# Configuracion de sitios soportados
SITES_CONFIG = {
    "remoteok": SiteConfig(
        name="RemoteOK",
        base_url="https://remoteok.com",
        requires_auth=False
    ),
    "infojobs": SiteConfig(
        name="InfoJobs",
        base_url="https://www.infojobs.net",
        requires_auth=True,
        credentials=get_credentials("INFOJOBS")
    ),
    "linkedin": SiteConfig(
        name="LinkedIn",
        base_url="https://www.linkedin.com",
        requires_auth=True,
        credentials=get_credentials("LINKEDIN")
    ),
    "indeed": SiteConfig(
        name="Indeed",
        base_url="https://www.indeed.com",
        requires_auth=False
    ),
    "tecnoempleo": SiteConfig(
        name="Tecnoempleo",
        base_url="https://www.tecnoempleo.com",
        requires_auth=False
    ),
}


# Configuracion general
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # Segundos entre requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",  # No incluir 'br' sin libreria brotli
    "Connection": "keep-alive",
}
