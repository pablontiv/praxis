"""
Procesa un CSV, filtra filas con status='active' y genera un reporte PDF
con gráficos de distribución por cada columna categórica detectada.

Uso:
    python csv_report.py datos.csv [--output reporte.pdf] [--status-col status]

Dependencias:
    pip install pandas matplotlib
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def load_and_filter(csv_path: str, status_col: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if status_col not in df.columns:
        sys.exit(f"Error: columna '{status_col}' no encontrada. Columnas disponibles: {list(df.columns)}")
    active = df[df[status_col].str.strip().str.lower() == "active"].copy()
    print(f"Total filas: {len(df):,} | Activas: {len(active):,} ({len(active)/len(df)*100:.1f}%)")
    return active


def detect_category_columns(df: pd.DataFrame, status_col: str, max_unique: int = 30) -> list[str]:
    """Detecta columnas categóricas con entre 2 y max_unique valores únicos."""
    skip = {status_col.lower(), "id", "index"}
    cols = []
    for col in df.columns:
        if col.lower() in skip:
            continue
        if df[col].dtype == "object" or df[col].nunique() <= max_unique:
            if 2 <= df[col].nunique() <= max_unique:
                cols.append(col)
    return cols


def generate_pdf(df: pd.DataFrame, category_cols: list[str], output_path: str):
    with PdfPages(output_path) as pdf:
        # Página de resumen
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        summary = (
            f"Reporte de registros activos\n"
            f"{'=' * 40}\n\n"
            f"Total registros activos: {len(df):,}\n"
            f"Columnas categóricas: {len(category_cols)}\n"
            f"  {', '.join(category_cols)}\n"
        )
        ax.text(0.05, 0.95, summary, transform=ax.transAxes,
                fontsize=13, verticalalignment="top", fontfamily="monospace")
        pdf.savefig(fig)
        plt.close(fig)

        # Para cada columna categórica: bar chart + pie chart
        for col in category_cols:
            counts = df[col].value_counts()
            n_cats = len(counts)

            # Agrupar en "Otros" si hay más de 20 categorías
            if n_cats > 20:
                other = counts[20:].sum()
                counts = pd.concat([counts[:20], pd.Series({"Otros": other})])

            # Barras horizontales
            fig, ax = plt.subplots(figsize=(10, max(6, len(counts) * 0.4)))
            counts.sort_values().plot.barh(ax=ax, color="#4C72B0", edgecolor="white")
            ax.set_xlabel("Cantidad")
            ax.set_title(f"Distribución por '{col}' (status=active)")
            for i, v in enumerate(counts.sort_values()):
                ax.text(v + counts.max() * 0.01, i, f"{v:,}", va="center", fontsize=8)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # Pie chart (top 10)
            top10 = counts.head(10)
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(
                top10, labels=top10.index, autopct="%1.1f%%",
                startangle=140, pctdistance=0.85
            )
            for t in autotexts:
                t.set_fontsize(8)
            ax.set_title(f"Top 10 — '{col}' (status=active)")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

            # Tabla de frecuencias
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            table_data = [[cat, f"{cnt:,}", f"{cnt/len(df)*100:.1f}%"]
                          for cat, cnt in counts.items()]
            table = ax.table(
                cellText=table_data,
                colLabels=["Categoría", "Cantidad", "% del total"],
                cellLoc="center", loc="upper center",
                colWidths=[0.45, 0.25, 0.2]
            )
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.4)
            for j in range(3):
                table[0, j].set_facecolor("#4C72B0")
                table[0, j].set_text_props(color="white", weight="bold")
            ax.set_title(f"Frecuencias — '{col}'", pad=20, fontsize=13)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"PDF generado: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Filtra CSV por status=active y genera reporte PDF")
    parser.add_argument("csv", help="Ruta al archivo CSV")
    parser.add_argument("-o", "--output", default="reporte.pdf", help="Ruta del PDF de salida (default: reporte.pdf)")
    parser.add_argument("--status-col", default="status", help="Nombre de la columna de status (default: status)")
    parser.add_argument("--max-unique", type=int, default=30,
                        help="Máximo de valores únicos para considerar una columna como categórica (default: 30)")
    args = parser.parse_args()

    if not Path(args.csv).exists():
        sys.exit(f"Error: archivo '{args.csv}' no encontrado")

    df = load_and_filter(args.csv, args.status_col)
    if df.empty:
        sys.exit("No se encontraron registros con status='active'")

    category_cols = detect_category_columns(df, args.status_col, args.max_unique)
    if not category_cols:
        sys.exit("No se detectaron columnas categóricas para graficar.")

    print(f"Columnas categóricas detectadas: {category_cols}")
    generate_pdf(df, category_cols, args.output)


if __name__ == "__main__":
    main()
