#!/usr/bin/env python3
"""
JobFy - Web Scraper Multi-sitio para ofertas de empleo
Extrae ofertas de trabajo desde multiples portales y las exporta a CSV.

Sitios soportados:
    - RemoteOK (sin login)
    - InfoJobs (requiere login)
    - LinkedIn (requiere login)
    - Indeed (sin login)
    - Tecnoempleo (sin login)

Uso:
    python jobfy_scraper.py [opciones]

Ejemplos:
    python jobfy_scraper.py --keyword "python" --location "Madrid"
    python jobfy_scraper.py --sites remoteok,indeed --keyword "react"
    python jobfy_scraper.py --all --keyword "data engineer"
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

from config import SITES_CONFIG, REQUEST_DELAY
from scrapers import (
    JobOffer,
    RemoteOKScraper,
    InfoJobsScraper,
    LinkedInScraper,
    IndeedScraper,
    TecnoempleoScraper,
)


# Mapeo de nombres a clases de scrapers
SCRAPERS = {
    "remoteok": RemoteOKScraper,
    "infojobs": InfoJobsScraper,
    "linkedin": LinkedInScraper,
    "indeed": IndeedScraper,
    "tecnoempleo": TecnoempleoScraper,
}

OUTPUT_DIR = "output"


def get_available_sites() -> list[str]:
    """Retorna lista de sitios disponibles."""
    return list(SCRAPERS.keys())


def print_banner() -> None:
    """Muestra el banner de la aplicacion."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       ██╗ ██████╗ ██████╗ ███████╗██╗   ██╗               ║
    ║       ██║██╔═══██╗██╔══██╗██╔════╝╚██╗ ██╔╝               ║
    ║       ██║██║   ██║██████╔╝█████╗   ╚████╔╝                ║
    ║  ██   ██║██║   ██║██╔══██╗██╔══╝    ╚██╔╝                 ║
    ║  ╚█████╔╝╚██████╔╝██████╔╝██║        ██║                  ║
    ║   ╚════╝  ╚═════╝ ╚═════╝ ╚═╝        ╚═╝                  ║
    ║                                                           ║
    ║          Multi-Site Job Scraper v2.0                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_site_status() -> None:
    """Muestra el estado de configuracion de cada sitio."""
    print("\n[INFO] Estado de sitios configurados:")
    print("-" * 50)

    for name, config in SITES_CONFIG.items():
        status = "OK"
        if config.requires_auth:
            if config.credentials:
                status = "OK (credenciales configuradas)"
            else:
                status = "PENDIENTE (requiere credenciales)"

        auth_icon = " [AUTH]" if config.requires_auth else ""
        print(f"  {config.name:15}{auth_icon:8} - {status}")

    print("-" * 50)


def save_to_csv(jobs: list[JobOffer], filepath: str) -> bool:
    """
    Guarda las ofertas de trabajo en un archivo CSV.

    Args:
        jobs: Lista de ofertas a guardar
        filepath: Ruta del archivo CSV

    Returns:
        True si se guardo correctamente, False en caso contrario
    """
    if not jobs:
        print("[WARNING] No hay ofertas para guardar")
        return False

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["job_title", "company", "location", "salary", "tags", "apply_link", "source"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for job in jobs:
                writer.writerow(job.to_dict())

        print(f"\n[OK] Guardadas {len(jobs)} ofertas en {filepath}")
        return True
    except IOError as e:
        print(f"[ERROR] No se pudo guardar el archivo: {e}")
        return False


def ensure_output_dir(directory: str) -> str:
    """Crea el directorio de salida si no existe y retorna la ruta."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, directory)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"[INFO] Creado directorio: {output_path}")

    return output_path


def run_scrapers(
    sites: list[str],
    keyword: str = "",
    location: str = ""
) -> list[JobOffer]:
    """
    Ejecuta los scrapers seleccionados y recolecta ofertas.

    Args:
        sites: Lista de sitios a scrapear
        keyword: Termino de busqueda
        location: Ubicacion

    Returns:
        Lista combinada de todas las ofertas
    """
    all_jobs = []

    for site_name in sites:
        if site_name not in SCRAPERS:
            print(f"[WARNING] Sitio '{site_name}' no reconocido, saltando...")
            continue

        scraper_class = SCRAPERS[site_name]

        try:
            scraper = scraper_class()
            jobs = scraper.scrape(keyword=keyword, location=location)
            all_jobs.extend(jobs)
            scraper.close()

            # Delay entre sitios para ser respetuosos
            if site_name != sites[-1]:
                print(f"  [INFO] Esperando {REQUEST_DELAY}s antes del siguiente sitio...")
                time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"[ERROR] Error con {site_name}: {e}")
            continue

    return all_jobs


def display_summary(jobs: list[JobOffer], sites: list[str]) -> None:
    """Muestra resumen de las ofertas encontradas."""
    print("\n" + "=" * 60)
    print("RESUMEN DE BUSQUEDA")
    print("=" * 60)

    # Contar por sitio
    jobs_by_source = {}
    for job in jobs:
        source = job.source
        jobs_by_source[source] = jobs_by_source.get(source, 0) + 1

    print(f"\nTotal de ofertas encontradas: {len(jobs)}")
    print("\nDesglose por sitio:")
    for source, count in sorted(jobs_by_source.items()):
        print(f"  - {source}: {count} ofertas")

    # Preview de ofertas
    if jobs:
        print("\n" + "-" * 60)
        print("Preview de las primeras ofertas:")
        print("-" * 60)

        for i, job in enumerate(jobs[:5], 1):
            print(f"\n{i}. {job.job_title}")
            print(f"   Empresa:   {job.company}")
            print(f"   Ubicacion: {job.location}")
            if job.salary != "N/A":
                print(f"   Salario:   {job.salary}")
            print(f"   Fuente:    {job.source}")


def parse_arguments() -> argparse.Namespace:
    """Parsea argumentos de linea de comandos."""
    parser = argparse.ArgumentParser(
        description="JobFy - Scraper multi-sitio de ofertas de empleo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --keyword "python developer" --location "Madrid"
  %(prog)s --sites remoteok,indeed --keyword "react"
  %(prog)s --all --keyword "data engineer"
  %(prog)s --list-sites

Sitios que requieren credenciales:
  Configura las variables de entorno en un archivo .env:
    INFOJOBS_USERNAME=tu_email
    INFOJOBS_PASSWORD=tu_password
    LINKEDIN_USERNAME=tu_email
    LINKEDIN_PASSWORD=tu_password
        """
    )

    parser.add_argument(
        "-k", "--keyword",
        type=str,
        default="",
        help="Termino de busqueda (ej: 'python developer', 'react')"
    )

    parser.add_argument(
        "-l", "--location",
        type=str,
        default="",
        help="Ubicacion (ej: 'Madrid', 'Barcelona', 'Remote')"
    )

    parser.add_argument(
        "-s", "--sites",
        type=str,
        default="remoteok",
        help="Sitios a scrapear separados por coma (ej: 'remoteok,indeed,tecnoempleo')"
    )

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Scrapear todos los sitios disponibles"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="",
        help="Nombre personalizado para el archivo CSV de salida"
    )

    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="Mostrar sitios disponibles y salir"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado de configuracion de sitios"
    )

    return parser.parse_args()


def main() -> None:
    """Punto de entrada principal."""
    args = parse_arguments()

    print_banner()

    # Mostrar lista de sitios
    if args.list_sites:
        print("\nSitios disponibles:")
        for name in get_available_sites():
            config = SITES_CONFIG[name]
            auth = " (requiere login)" if config.requires_auth else ""
            print(f"  - {name}{auth}")
        sys.exit(0)

    # Mostrar estado
    if args.status:
        print_site_status()
        sys.exit(0)

    # Determinar sitios a scrapear
    if args.all:
        sites = get_available_sites()
    else:
        sites = [s.strip().lower() for s in args.sites.split(",")]

    # Validar sitios
    valid_sites = []
    for site in sites:
        if site in SCRAPERS:
            valid_sites.append(site)
        else:
            print(f"[WARNING] Sitio '{site}' no reconocido")

    if not valid_sites:
        print("[ERROR] No hay sitios validos para scrapear")
        sys.exit(1)

    # Mostrar configuracion
    print(f"\n[CONFIG] Sitios seleccionados: {', '.join(valid_sites)}")
    if args.keyword:
        print(f"[CONFIG] Busqueda: '{args.keyword}'")
    if args.location:
        print(f"[CONFIG] Ubicacion: '{args.location}'")

    print_site_status()

    # Ejecutar scraping
    print("\n" + "=" * 60)
    print("INICIANDO SCRAPING")
    print("=" * 60)

    jobs = run_scrapers(valid_sites, args.keyword, args.location)

    # Guardar resultados
    if jobs:
        output_path = ensure_output_dir(OUTPUT_DIR)

        # Nombre del archivo
        if args.output:
            filename = args.output if args.output.endswith(".csv") else f"{args.output}.csv"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            keyword_slug = args.keyword.replace(" ", "_")[:20] if args.keyword else "all"
            filename = f"jobs_{keyword_slug}_{timestamp}.csv"

        csv_path = os.path.join(output_path, filename)
        save_to_csv(jobs, csv_path)

        display_summary(jobs, valid_sites)
        print(f"\n[OK] Archivo guardado: {csv_path}")
    else:
        print("\n[WARNING] No se encontraron ofertas de trabajo")

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETADO")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
