"""
Endpoints de reportes — devuelven JSON con los datos procesados.

Cada endpoint descarga los datos de la API (o usa el caché), ejecuta el reporte
y devuelve el resultado como JSON listo para que Svelte lo grafique.
"""
from fastapi import APIRouter, Query

from data.fetcher import fetch_all_interactions
from reports.by_country import report_by_country
from reports.by_type import report_by_type
from reports.time_analysis import report_time_analysis
from reports.user_journey import report_user_journey
from reports.traffic_sources import report_traffic_sources

router = APIRouter()

# Cache en memoria para no descargar datos en cada request
_df_cache = {"df": None}


def _get_df():
    """Obtiene el DataFrame, cacheado en memoria."""
    if _df_cache["df"] is None:
        _df_cache["df"] = fetch_all_interactions()
    return _df_cache["df"]


@router.post("/refresh")
def refresh_data():
    """Fuerza la recarga de datos desde la API."""
    _df_cache["df"] = None
    _df_cache["df"] = fetch_all_interactions()
    return {"status": "ok", "total_rows": len(_df_cache["df"])}


@router.get("/country")
def get_report_country(top_n: int = Query(default=15, ge=1, le=100)):
    """Interacciones por país."""
    df = _get_df()
    result = report_by_country(df, top_n=top_n, save=False)
    return {
        "report": "by_country",
        "total_countries": len(result),
        "data": result.to_dict(orient="records"),
    }


@router.get("/type")
def get_report_type():
    """Interacciones por tipo de evento."""
    df = _get_df()
    result = report_by_type(df, save=False)
    return {
        "report": "by_type",
        "data": result.to_dict(orient="records"),
    }


@router.get("/time")
def get_report_time():
    """Análisis de tiempos entre interacciones del mismo usuario."""
    df = _get_df()
    result = report_time_analysis(df, save=False)
    return {
        "report": "time_analysis",
        "total_users_with_gaps": len(result),
        "data": result.to_dict(orient="records"),
    }


@router.get("/journey")
def get_report_journey(top_n: int = Query(default=15, ge=1, le=100)):
    """Caminos de usuario más frecuentes."""
    df = _get_df()
    result = report_user_journey(df, top_n=top_n, save=False)
    return {
        "report": "user_journey",
        "total_unique_journeys": len(result),
        "data": result.head(top_n).to_dict(orient="records"),
    }


@router.get("/recent")
def get_report_recent(top_n: int = Query(default=50, ge=1, le=500)):
    """Últimas interacciones registradas, de más nueva a más antigua."""
    df = _get_df()
    cols = ["id", "type", "timestamp_utc", "country_iso", "ga_client_id", "search_method",
            "utm_source", "utm_medium", "utm_campaign", "gclid", "fbclid"]
    available = [c for c in cols if c in df.columns]
    result = (
        df[available]
        .sort_values("timestamp_utc", ascending=False)
        .head(top_n)
    )
    data = result.to_dict(orient="records")
    import math
    for row in data:
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                row[k] = None

    return {
        "report": "recent",
        "total_returned": len(result),
        "data": data,
    }


@router.get("/traffic")
def get_report_traffic(top_n: int = Query(default=10, ge=1, le=100)):
    """Fuentes de tráfico (UTM, Google Ads, Facebook Ads)."""
    df = _get_df()
    results = report_traffic_sources(df, top_n=top_n, save=False)
    return {
        "report": "traffic_sources",
        "source": results["source"].head(top_n).to_dict(orient="records"),
        "medium": results["medium"].head(top_n).to_dict(orient="records"),
        "campaign": results["campaign"].head(top_n).to_dict(orient="records"),
        "ad_platform": results["ad_platform"].to_dict(orient="records"),
    }
