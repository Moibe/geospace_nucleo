"""
Reporte: Análisis de tiempos entre interacciones del mismo usuario.

Lógica:
  - Se agrupa por ga_client_id (identifica al mismo navegador/usuario).
  - Se ordena por timestamp_utc.
  - Para cada usuario se calcula el tiempo (segundos) entre cada par
    de interacciones consecutivas.
  - Se filtran gaps < 30 min (1800 s) para descartar sesiones separadas.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import OUTPUT_DIR

MAX_GAP_SECONDS = 1800  # 30 minutos → límite de sesión


def report_time_analysis(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """
    Calcula el tiempo entre interacciones consecutivas del mismo usuario.
    Devuelve un DataFrame con estadísticas por usuario.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    work = df[df["ga_client_id"].notna()].copy()
    work = work.sort_values(["ga_client_id", "timestamp_utc"])

    work["prev_ts"] = work.groupby("ga_client_id")["timestamp_utc"].shift(1)
    work["gap_seconds"] = (
        work["timestamp_utc"] - work["prev_ts"]
    ).dt.total_seconds()

    # Solo gaps dentro de una misma sesión
    within_session = work[
        (work["gap_seconds"].notna()) &
        (work["gap_seconds"] > 0) &
        (work["gap_seconds"] <= MAX_GAP_SECONDS)
    ]

    # Estadísticas globales
    stats = within_session["gap_seconds"].describe()

    if save:
        print("\n  [Tiempos entre interacciones — misma sesión]")
        print(f"  Mediana : {stats['50%']:.1f} s")
        print(f"  Media   : {stats['mean']:.1f} s")
        print(f"  Máximo  : {stats['max']:.1f} s")

        # ── Histograma ─────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(within_session["gap_seconds"], bins=40, color="#4C9BE8", edgecolor="white")
        ax.set_xlabel("Segundos entre interacciones")
        ax.set_ylabel("Frecuencia")
        ax.set_title("Distribución del tiempo entre interacciones (≤ 30 min)")
        ax.axvline(stats["mean"], color="red", linestyle="--", label=f"Media: {stats['mean']:.0f}s")
        ax.axvline(stats["50%"], color="orange", linestyle="--", label=f"Mediana: {stats['50%']:.0f}s")
        ax.legend()
        plt.tight_layout()

        path = os.path.join(OUTPUT_DIR, "time_analysis.png")
        fig.savefig(path, dpi=150)
        print(f"  Gráfico guardado: {path}")
        plt.close(fig)

    # Resumen por usuario
    summary = (
        within_session.groupby("ga_client_id")["gap_seconds"]
        .agg(["count", "mean", "median", "max"])
        .rename(columns={"count": "n_gaps", "mean": "avg_s", "median": "median_s", "max": "max_s"})
        .round(1)
        .reset_index()
    )

    if save:
        summary.to_excel(os.path.join(OUTPUT_DIR, "time_analysis.xlsx"), index=False)
        print(f"  Excel guardado: {os.path.join(OUTPUT_DIR, 'time_analysis.xlsx')}")

    return summary
