"""
Reporte: Fuentes de tráfico.

Analiza:
  - utm_source / utm_medium / utm_campaign
  - Presencia de gclid (Google Ads) y fbclid (Facebook Ads)
  - Combinación de fuente + medio más frecuente
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import OUTPUT_DIR


def report_traffic_sources(df: pd.DataFrame, top_n: int = 10, save: bool = True) -> dict:
    """
    Genera reportes de fuentes de tráfico.
    Devuelve un dict con DataFrames: 'source', 'medium', 'campaign', 'ad_platform'.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {}

    # ── UTM Source ─────────────────────────────────────────────────────────────
    source = (
        df["utm_source"].fillna("(direct)").value_counts()
        .reset_index()
    )
    source.columns = ["utm_source", "interactions"]
    results["source"] = source

    # ── UTM Medium ─────────────────────────────────────────────────────────────
    medium = (
        df["utm_medium"].fillna("(none)").value_counts()
        .reset_index()
    )
    medium.columns = ["utm_medium", "interactions"]
    results["medium"] = medium

    # ── UTM Campaign ───────────────────────────────────────────────────────────
    campaign = (
        df["utm_campaign"].fillna("(none)").value_counts()
        .reset_index()
    )
    campaign.columns = ["utm_campaign", "interactions"]
    results["campaign"] = campaign

    # ── Plataforma de anuncio (gclid / fbclid) ─────────────────────────────────
    df_copy = df.copy()
    def ad_platform(row):
        if pd.notna(row.get("gclid")):
            return "Google Ads"
        if pd.notna(row.get("fbclid")):
            return "Facebook Ads"
        return "Organic / Direct"

    df_copy["ad_platform"] = df_copy.apply(ad_platform, axis=1)
    platform = df_copy["ad_platform"].value_counts().reset_index()
    platform.columns = ["ad_platform", "interactions"]
    results["ad_platform"] = platform

    # ── Gráfico de 4 subplots ──────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Fuentes de tráfico", fontsize=14, fontweight="bold")

    def _bar(ax, data, label_col, title):
        top = data.head(top_n)
        ax.barh(top[label_col][::-1], top["interactions"][::-1], color="#E87B4C")
        ax.set_title(title)
        ax.set_xlabel("Interacciones")

    _bar(axes[0, 0], source,   "utm_source",   "UTM Source")
    _bar(axes[0, 1], medium,   "utm_medium",   "UTM Medium")
    _bar(axes[1, 0], campaign, "utm_campaign", "UTM Campaign")
    _bar(axes[1, 1], platform, "ad_platform",  "Plataforma de anuncio")

    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, "traffic_sources.png")
        fig.savefig(path, dpi=150)
        print(f"  Gráfico guardado: {path}")

        with pd.ExcelWriter(os.path.join(OUTPUT_DIR, "traffic_sources.xlsx")) as writer:
            for sheet, frame in results.items():
                frame.to_excel(writer, sheet_name=sheet, index=False)
        print(f"  Excel guardado: {os.path.join(OUTPUT_DIR, 'traffic_sources.xlsx')}")

    plt.close(fig)
    return results
