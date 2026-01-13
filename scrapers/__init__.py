"""Modulo de scrapers para diferentes sitios de empleo."""

from .base import BaseScraper, JobOffer
from .remoteok import RemoteOKScraper
from .infojobs import InfoJobsScraper
from .linkedin import LinkedInScraper
from .indeed import IndeedScraper
from .tecnoempleo import TecnoempleoScraper

__all__ = [
    "BaseScraper",
    "JobOffer",
    "RemoteOKScraper",
    "InfoJobsScraper",
    "LinkedInScraper",
    "IndeedScraper",
    "TecnoempleoScraper",
]
