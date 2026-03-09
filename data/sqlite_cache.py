"""
Caché local en SQLite: descarga los datos de la API y los guarda en un archivo .db
para que Vanna.ai pueda hacer queries SQL sin conexión a la red.
"""
import sqlite3
import os

import pandas as pd

from config.settings import SQLITE_DB_PATH
from data.fetcher import fetch_all_interactions


def build_sqlite_cache(force: bool = False) -> str:
    """
    Descarga todos los datos de la API y los guarda en SQLite.
    Si el archivo ya existe y force=False, no lo reconstruye.
    Devuelve la ruta al archivo .db
    """
    if os.path.exists(SQLITE_DB_PATH) and not force:
        print(f"SQLite cache ya existe: {SQLITE_DB_PATH}")
        return SQLITE_DB_PATH

    print("Construyendo caché SQLite...")
    df = fetch_all_interactions()

    # Convertir datetimes a string para SQLite
    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].astype(str)

    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    df.to_sql("map_interactions", conn, if_exists="replace", index=False)
    conn.close()

    print(f"SQLite cache creado: {SQLITE_DB_PATH} ({len(df)} registros)")
    return SQLITE_DB_PATH


def get_sqlite_ddl() -> str:
    """Devuelve el DDL (CREATE TABLE) de la tabla en SQLite para entrenar a Vanna."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='map_interactions'"
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""
