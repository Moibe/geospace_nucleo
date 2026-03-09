"""
Reporte: Distribución de interacciones por país.

Columnas usadas:
  - country_iso         → código ISO declarado por el cliente
  - ip_detection_iso_code → código ISO detectado por IP
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import OUTPUT_DIR


def report_by_country(df: pd.DataFrame, top_n: int = 15, save: bool = True) -> pd.DataFrame:
    """
    Cuenta interacciones agrupadas por país (ip_detection_iso_code).
    Genera un gráfico de barras horizontal y devuelve el DataFrame con los conteos.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    col = "ip_detection_iso_code"
    counts = (
        df[col]
        .fillna("UNKNOWN")
        .value_counts()
        .reset_index()
    )
    counts.columns = ["country_iso", "interactions"]
    counts["pct"] = (counts["interactions"] / counts["interactions"].sum() * 100).round(2)

    # ── Gráfico ────────────────────────────────────────────────────────────────
    top = counts.head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top["country_iso"][::-1], top["interactions"][::-1], color="#4C9BE8")
    ax.set_xlabel("Interacciones")
    ax.set_title(f"Top {top_n} países por interacciones")
    for i, (v, p) in enumerate(zip(top["interactions"][::-1], top["pct"][::-1])):
        ax.text(v + 1, i, f"{v:,} ({p}%)", va="center", fontsize=9)
    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, "by_country.png")
        fig.savefig(path, dpi=150)
        print(f"  Gráfico guardado: {path}")
        counts.to_excel(os.path.join(OUTPUT_DIR, "by_country.xlsx"), index=False)
        print(f"  Excel guardado: {os.path.join(OUTPUT_DIR, 'by_country.xlsx')}")

    plt.close(fig)
    return counts
