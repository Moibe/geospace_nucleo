"""
Geospace Nucleo — FastAPI principal.

Endpoints:
  GET  /                         → health check
  GET  /api/reports/country      → reporte por país (JSON)
  GET  /api/reports/type         → reporte por tipo de interacción (JSON)
  GET  /api/reports/time         → análisis de tiempos entre interacciones (JSON)
  GET  /api/reports/journey      → caminos de usuario (JSON)
  GET  /api/reports/traffic      → fuentes de tráfico (JSON)
  POST /api/ask                  → pregunta en lenguaje natural (Vanna.ai)
  POST /api/refresh              → refrescar caché SQLite (solo local)
"""
import matplotlib
matplotlib.use("Agg")  # Backend no-GUI, seguro para threads

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import ENVIRONMENT


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos al arrancar la app."""
    # Asegurar que el caché SQLite exista en modo local
    if ENVIRONMENT != "production":
        from data.sqlite_cache import build_sqlite_cache
        build_sqlite_cache()

    # Crear agente Vanna y guardarlo en app.state
    from data.vanna_engine import create_agent
    app.state.vanna_agent = create_agent()

    print(f"Geospace Nucleo API iniciada [ambiente: {ENVIRONMENT}]")
    yield


app = FastAPI(
    title="Geospace Nucleo API",
    description="API de reportes y consultas en lenguaje natural para datos geoespaciales",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permitir acceso desde el frontend Svelte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "environment": ENVIRONMENT}


# Registrar routers
from api.routes.reports import router as reports_router
from api.routes.ask import router as ask_router

app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(ask_router, prefix="/api", tags=["ask"])
