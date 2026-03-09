"""
Entry point del proyecto Geospace Nucleo.

Uso:
    python main.py              → ejecuta todos los reportes
    python main.py --report country   → solo reporte de país
    python main.py --report type
    python main.py --report time
    python main.py --report journey
    python main.py --report traffic
"""
import argparse
import sys

from data.fetcher import fetch_all_interactions, fetch_stats
from reports.by_country import report_by_country
from reports.by_type import report_by_type
from reports.time_analysis import report_time_analysis
from reports.user_journey import report_user_journey
from reports.traffic_sources import report_traffic_sources

ALL_REPORTS = ["country", "type", "time", "journey", "traffic"]


def run_all(df):
    print("\n[1/5] Reporte por país...")
    report_by_country(df)

    print("\n[2/5] Reporte por tipo de interacción...")
    report_by_type(df)

    print("\n[3/5] Análisis de tiempos entre interacciones...")
    report_time_analysis(df)

    print("\n[4/5] Caminos de usuario...")
    report_user_journey(df)

    print("\n[5/5] Fuentes de tráfico...")
    report_traffic_sources(df)


def main():
    parser = argparse.ArgumentParser(description="Geospace analytics reports")
    parser.add_argument(
        "--report",
        choices=ALL_REPORTS + ["all"],
        default="all",
        help="Reporte a ejecutar (default: all)",
    )
    args = parser.parse_args()

    # Estadísticas rápidas
    stats = fetch_stats()
    print(f"Base de datos: {stats.get('database')} | Total interacciones: {stats.get('total_interactions'):,}")

    # Descarga de datos
    df = fetch_all_interactions()

    report = args.report
    if report == "all":
        run_all(df)
    elif report == "country":
        report_by_country(df)
    elif report == "type":
        report_by_type(df)
    elif report == "time":
        report_time_analysis(df)
    elif report == "journey":
        report_user_journey(df)
    elif report == "traffic":
        report_traffic_sources(df)

    print("\nListo. Archivos guardados en output/")


if __name__ == "__main__":
    main()
