"""
Módulo encargado de obtener todos los datos desde la API de Geospace.
Maneja la paginación automáticamente y devuelve un DataFrame con todos los registros.
"""
import requests
import pandas as pd

from config.settings import ENDPOINTS, FETCH_PAGE_SIZE


def fetch_all_interactions() -> pd.DataFrame:
    """
    Descarga todas las interacciones de la API paginando automáticamente.
    Devuelve un DataFrame con todos los registros y columnas de tiempo parseadas.
    """
    all_records = []
    skip = 0

    print("Descargando interacciones desde la API...")

    while True:
        url = f"{ENDPOINTS['interactions']}?limit={FETCH_PAGE_SIZE}&skip={skip}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        payload = response.json()

        batch = payload.get("data", [])
        if not batch:
            break

        all_records.extend(batch)
        total = payload.get("total", 0)
        skip += len(batch)

        print(f"  {skip}/{total} registros obtenidos...")

        if skip >= total:
            break

    print(f"Descarga completa: {len(all_records)} interacciones.")

    df = pd.DataFrame(all_records)

    # Parsear columnas de tiempo
    for col in ["timestamp_utc", "timestamp_cdmx", "created_at", "updated_at"]:
        if col in df.columns:
            # Las columnas tienen el formato "2026-03-09T16:46:14" o con sufijo de zona
            df[col] = pd.to_datetime(df[col].str.split(" ").str[0], errors="coerce")

    # Convertir coordenadas a float
    for col in [
        "location_shown_lat", "location_shown_lng",
        "ip_detection_lat", "ip_detection_lng",
        "gps_detection_lat", "gps_detection_lng",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def fetch_stats() -> dict:
    """Devuelve las estadísticas generales de la API."""
    response = requests.get(ENDPOINTS["stats"], timeout=10)
    response.raise_for_status()
    return response.json()
