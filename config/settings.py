from dotenv import load_dotenv
import os

# Cargar .env desde la raíz del proyecto
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

# ── Ambiente ───────────────────────────────────────────────────────────────────
# "local" = SQLite (datos descargados de la API)
# "production" = MariaDB (conexión directa)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

# ── API de datos (usada en modo local para descargar datos) ────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://moibe-fastapi-mariadb-geospaces.hf.space")

ENDPOINTS = {
    "interactions": f"{API_BASE_URL}/api/map-interactions",
    "stats":        f"{API_BASE_URL}/api/stats",
    "by_country":   f"{API_BASE_URL}/api/map-interactions/country",
}

# Tamaño de página al paginar la API
FETCH_PAGE_SIZE = 1000

# ── Rutas locales ──────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "geospace.db")

# ── LLM (Vanna.ai) ────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── MariaDB (solo en producción) ───────────────────────────────────────────────
MARIADB_HOST = os.getenv("MARIADB_HOST", "")
MARIADB_PORT = os.getenv("MARIADB_PORT", "3306")
MARIADB_USER = os.getenv("MARIADB_USER", "")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD", "")
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE", "")
