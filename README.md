# JobFy - Multi-Site Job Scraper

Herramienta de scraping en Python que extrae ofertas de trabajo desde multiples portales de empleo y las exporta a formato CSV.

## Sitios Soportados

| Sitio | Login | Estado | Descripcion |
|-------|-------|--------|-------------|
| **RemoteOK** | No | Funciona | Trabajos remotos globales (usa API JSON) |
| **Tecnoempleo** | No | Funciona | Empleo IT en Espana |
| InfoJobs | Si | Opcional | Principal portal en Espana |
| LinkedIn | Si | Opcional | Red profesional global |
| Indeed | No | Bloqueado | Proteccion anti-bot activa |

> **Recomendado:** Usa RemoteOK y Tecnoempleo para empezar. No requieren configuracion adicional.

## Inicio Rapido

```bash
# Clonar e instalar
git clone https://github.com/tu-usuario/JobFy.git
cd JobFy
python -m venv venv
source venv/bin/activate  # Linux/Mac (o venv\Scripts\activate en Windows)
pip install -r requirements.txt

# Ejecutar busqueda
python jobfy_scraper.py -s remoteok,tecnoempleo -k "python"
```

## Tecnologias

- **Python 3.10+**
- **requests** - Peticiones HTTP
- **BeautifulSoup4** - Parsing HTML
- **python-dotenv** - Variables de entorno
- **argparse** - Interfaz CLI

## Uso

### Busquedas basicas (sin configuracion)

```bash
# Buscar "python" en RemoteOK y Tecnoempleo
python jobfy_scraper.py -s remoteok,tecnoempleo -k "python"

# Buscar con ubicacion
python jobfy_scraper.py -s tecnoempleo -k "java" -l "Madrid"

# Solo RemoteOK (trabajos remotos)
python jobfy_scraper.py -k "react"
```

### Opciones CLI

| Opcion | Corto | Descripcion |
|--------|-------|-------------|
| `--keyword` | `-k` | Termino de busqueda |
| `--location` | `-l` | Ubicacion/ciudad |
| `--sites` | `-s` | Sitios separados por coma |
| `--all` | `-a` | Usar todos los sitios |
| `--output` | `-o` | Nombre del archivo CSV |
| `--list-sites` | | Listar sitios disponibles |
| `--status` | | Ver estado de configuracion |

### Comandos utiles

```bash
# Ver ayuda completa
python jobfy_scraper.py --help

# Ver sitios disponibles
python jobfy_scraper.py --list-sites

# Ver estado de configuracion
python jobfy_scraper.py --status
```

## Ejemplo de Salida

```
╔═══════════════════════════════════════════════════════════╗
║       ██╗ ██████╗ ██████╗ ███████╗██╗   ██╗               ║
║       ██║██╔═══██╗██╔══██╗██╔════╝╚██╗ ██╔╝               ║
║       ██║██║   ██║██████╔╝█████╗   ╚████╔╝                ║
║  ██   ██║██║   ██║██╔══██╗██╔══╝    ╚██╔╝                 ║
║  ╚█████╔╝╚██████╔╝██████╔╝██║        ██║                  ║
║   ╚════╝  ╚═════╝ ╚═════╝ ╚═╝        ╚═╝                  ║
║          Multi-Site Job Scraper v2.0                      ║
╚═══════════════════════════════════════════════════════════╝

[CONFIG] Sitios seleccionados: remoteok, tecnoempleo
[CONFIG] Busqueda: 'python'

============================================================
INICIANDO SCRAPING
============================================================

[RemoteOK] Iniciando scraping...
  [INFO] URL: https://remoteok.com/api
  [OK] Encontradas 3 ofertas

[Tecnoempleo] Iniciando scraping...
  [INFO] URL: https://www.tecnoempleo.com/busqueda-empleo.php?te=python
  [OK] Encontradas 30 ofertas

============================================================
RESUMEN DE BUSQUEDA
============================================================

Total de ofertas encontradas: 33

Desglose por sitio:
  - RemoteOK: 3 ofertas
  - Tecnoempleo: 30 ofertas

[OK] Archivo guardado: output/jobs_python_20240115_143052.csv
```

### CSV Generado

```csv
job_title,company,location,salary,tags,apply_link,source
Senior Python Developer,Cresta,Toronto,"$100,000 - $150,000","python, django, aws",https://remoteok.com/...,RemoteOK
Desarrollador Python,TechCorp,Espana,N/A,IT/Tech,https://tecnoempleo.com/...,Tecnoempleo
```

## Configuracion Opcional (InfoJobs/LinkedIn)

> **Advertencia:** InfoJobs y LinkedIn pueden bloquear cuentas por uso automatizado. Usa bajo tu responsabilidad.

Si deseas usar sitios que requieren login:

### 1. Crear archivo de credenciales

```bash
cp .env.example .env
```

### 2. Editar `.env` con tus datos

```env
# InfoJobs
INFOJOBS_USERNAME=tu_email@ejemplo.com
INFOJOBS_PASSWORD=tu_password

# LinkedIn
LINKEDIN_USERNAME=tu_email@ejemplo.com
LINKEDIN_PASSWORD=tu_password
```

### 3. Ejecutar con todos los sitios

```bash
python jobfy_scraper.py --all -k "data engineer"
```

### Seguridad

- El archivo `.env` esta en `.gitignore` y **nunca se sube a GitHub**
- Solo `.env.example` (sin datos reales) se incluye en el repositorio
- Cada usuario debe crear su propio `.env` localmente

## Estructura del Proyecto

```
JobFy/
├── jobfy_scraper.py      # Script principal CLI
├── config.py             # Configuracion y credenciales
├── requirements.txt      # Dependencias
├── .env.example          # Plantilla (sin datos reales)
├── .gitignore            # Excluye .env y otros
├── README.md
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Clase base abstracta
│   ├── remoteok.py       # API JSON de RemoteOK
│   ├── tecnoempleo.py    # Scraper Tecnoempleo
│   ├── infojobs.py       # Scraper InfoJobs (requiere login)
│   ├── linkedin.py       # Scraper LinkedIn (requiere login)
│   └── indeed.py         # Scraper Indeed (bloqueado)
└── output/
    └── *.csv             # Archivos generados
```

## Arquitectura

El proyecto usa el patron **Template Method** con una clase base abstracta:

```python
class BaseScraper(ABC):
    @abstractmethod
    def _perform_login(self) -> bool: ...

    @abstractmethod
    def get_search_url(self, keyword, location) -> str: ...

    @abstractmethod
    def parse_job_listings(self, html) -> list[JobOffer]: ...

    def scrape(self, keyword, location) -> list[JobOffer]:
        # Logica comun: login -> fetch -> parse
```

Esto permite agregar nuevos sitios facilmente heredando de `BaseScraper`.

## Agregar Nuevos Sitios

1. Crear `scrapers/nuevo_sitio.py`
2. Heredar de `BaseScraper`
3. Implementar los metodos abstractos
4. Registrar en `config.py` y `jobfy_scraper.py`

```python
from .base import BaseScraper, JobOffer

class NuevoSitioScraper(BaseScraper):
    def _perform_login(self) -> bool:
        return True  # o implementar login

    def get_search_url(self, keyword: str, location: str) -> str:
        return f"https://nuevositio.com/jobs?q={keyword}"

    def parse_job_listings(self, html: str) -> list[JobOffer]:
        # Implementar parsing con BeautifulSoup
        ...
```

## Limitaciones

- **Indeed:** Actualmente bloqueado por proteccion anti-bot (error 403)
- **InfoJobs/LinkedIn:** Pueden mostrar captchas o bloquear cuentas
- **Estructura HTML:** Los sitios cambian frecuentemente sus selectores
- **Rate limiting:** Requests excesivos pueden resultar en bloqueos temporales

## Disclaimer - Uso Etico

Este proyecto es **exclusivamente con fines educativos y de portfolio**.

- Revisa los **Terminos de Servicio** de cada sitio
- **LinkedIn tiene politicas muy estrictas** contra el scraping
- Respeta el archivo `robots.txt`
- No uses los datos con **fines comerciales** sin autorizacion
- Considera usar **APIs oficiales** cuando esten disponibles:
  - [LinkedIn API](https://developer.linkedin.com/)
  - [Indeed API](https://developer.indeed.com/)

**El autor no se hace responsable del uso indebido de esta herramienta.**

## Mejoras Futuras

- [ ] Paginacion (multiples paginas de resultados)
- [ ] Exportacion a JSON y SQLite
- [ ] Filtrado por salario minimo
- [ ] Notificaciones (email/Telegram)
- [ ] Interfaz web con Flask/FastAPI
- [ ] Tests unitarios

## Licencia

MIT License - Libre para uso personal y educativo.

---

Desarrollado como proyecto de portfolio | Python & Web Scraping
