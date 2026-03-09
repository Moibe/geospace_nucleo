"""
Reporte: Distribución de interacciones por tipo de evento.

Columna usada:
  - type  → e.g. organic_visit, ad_visit, ...
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import OUTPUT_DIR


def report_by_type(df: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    """
    Cuenta interacciones por tipo y genera un gráfico de torta + barras.
    Devuelve el DataFrame con los conteos.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    counts = (
        df["type"]
        .fillna("UNKNOWN")
        .value_counts()
        .reset_index()
    )
    counts.columns = ["type", "interactions"]
    counts["pct"] = (counts["interactions"] / counts["interactions"].sum() * 100).round(2)

    # ── Gráfico ────────────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Torta
    ax1.pie(
        counts["interactions"],
        labels=counts["type"],
        autopct="%1.1f%%",
        startangle=140,
        colors=plt.cm.tab10.colors,
    )
    ax1.set_title("Proporción por tipo")

    # Barras
    ax2.bar(counts["type"], counts["interactions"], color=plt.cm.tab10.colors)
    ax2.set_xlabel("Tipo")
    ax2.set_ylabel("Interacciones")
    ax2.set_title("Interacciones por tipo")
    ax2.tick_params(axis="x", rotation=20)
    for i, v in enumerate(counts["interactions"]):
        ax2.text(i, v + 0.5, str(v), ha="center", fontsize=9)

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, "by_type.png")
        fig.savefig(path, dpi=150)
        print(f"  Gráfico guardado: {path}")
        counts.to_excel(os.path.join(OUTPUT_DIR, "by_type.xlsx"), index=False)
        print(f"  Excel guardado: {os.path.join(OUTPUT_DIR, 'by_type.xlsx')}")

    plt.close(fig)
    return counts
