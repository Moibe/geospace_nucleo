"""
Reporte: Camino (journey) que sigue cada usuario.

Lógica:
  - Se agrupa por ga_client_id, ordenando por timestamp_utc.
  - La secuencia de valores de `type` forma el "camino".
  - Se cuentan los caminos más frecuentes.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from config.settings import OUTPUT_DIR


def report_user_journey(df: pd.DataFrame, top_n: int = 15, save: bool = True) -> pd.DataFrame:
    """
    Construye el camino de cada usuario (secuencia de tipos de interacción)
    y devuelve los caminos más frecuentes.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    work = df[df["ga_client_id"].notna()].copy()
    work = work.sort_values(["ga_client_id", "timestamp_utc"])

    # Construir el camino como string " → a → b → c"
    journeys = (
        work.groupby("ga_client_id")["type"]
        .apply(lambda seq: " → ".join(seq.astype(str)))
        .reset_index()
    )
    journeys.columns = ["ga_client_id", "journey"]

    # Contar caminos frecuentes
    journey_counts = (
        journeys["journey"]
        .value_counts()
        .reset_index()
    )
    journey_counts.columns = ["journey", "users"]
    journey_counts["pct"] = (
        journey_counts["users"] / journey_counts["users"].sum() * 100
    ).round(2)

    top = journey_counts.head(top_n)

    # ── Gráfico ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, max(5, len(top) * 0.5)))
    labels = [j if len(j) <= 60 else j[:57] + "..." for j in top["journey"][::-1]]
    ax.barh(labels, top["users"][::-1], color="#6DBF9E")
    ax.set_xlabel("Usuarios")
    ax.set_title(f"Top {top_n} caminos de usuario más frecuentes")
    for i, (v, p) in enumerate(zip(top["users"][::-1], top["pct"][::-1])):
        ax.text(v + 0.1, i, f"{v} ({p}%)", va="center", fontsize=8)
    plt.tight_layout()

    if save:
        path = os.path.join(OUTPUT_DIR, "user_journey.png")
        fig.savefig(path, dpi=150)
        print(f"  Gráfico guardado: {path}")
        journey_counts.to_excel(os.path.join(OUTPUT_DIR, "user_journey.xlsx"), index=False)
        print(f"  Excel guardado: {os.path.join(OUTPUT_DIR, 'user_journey.xlsx')}")

    plt.close(fig)
    return journey_counts
