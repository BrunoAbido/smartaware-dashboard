import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

# Mapeamento de períodos para horários
period_to_time = {
    1: "08:00 – 09:00", 2: "09:00 – 10:00", 3: "10:00 – 11:00",
    4: "11:00 – 12:00", 5: "12:00 – 13:00", 6: "13:00 – 14:00",
    7: "14:00 – 15:00", 8: "15:00 – 16:00", 9: "16:00 – 17:00",
    10: "17:00 – 18:00", 11: "18:00 – 19:00", 12: "19:00 – 20:00"
}

def read_csv_safely(path):
    """Lê CSVs de forma segura."""
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return None


def generate_daily_report(date_str, output_path="relatorio_dia.pdf"):
    """
    Gera o relatório PDF completo com base em:
    - Entradas do dia (people_total.csv)
    - Tempos de fila (queue_time1.csv e queue_time2.csv)
    """

    # Caminhos dos arquivos
    people_total_path = os.path.join(BASE_DIR, "camera11", date_str, "count", "people_total.csv")
    queue1_path = os.path.join(BASE_DIR, "camera11", date_str, "queue", "queue_time1.csv")
    queue2_path = os.path.join(BASE_DIR, "camera11", date_str, "queue", "queue_time2.csv")

    # Lê CSVs
    df_total = read_csv_safely(people_total_path)
    df_q1 = read_csv_safely(queue1_path)
    df_q2 = read_csv_safely(queue2_path)

    if df_total is None or df_q1 is None or df_q2 is None:
        raise FileNotFoundError("Um ou mais arquivos necessários não foram encontrados.")

    # Normaliza colunas
    for df in [df_total, df_q1, df_q2]:
        if "Período" in df.columns:
            df["Período"] = df["Período"].astype(str).str.strip()

    # Remove linha "Total" para cálculo detalhado
    df_total_filtered = df_total[df_total["Período"].str.lower() != "total"].copy()
    df_q1_filtered = df_q1[df_q1["Período"].astype(str).str.lower() != "total"].copy()
    df_q2_filtered = df_q2[df_q2["Período"].astype(str).str.lower() != "total"].copy()

    # Converte períodos em int
    df_total_filtered["Período"] = df_total_filtered["Período"].astype(int)
    df_q1_filtered["Período"] = df_q1_filtered["Período"].astype(int)
    df_q2_filtered["Período"] = df_q2_filtered["Período"].astype(int)

    # Junta as tabelas pelo período
    merged = pd.DataFrame({"Período": sorted(period_to_time.keys())})
    merged = merged.merge(df_total_filtered[["Período", "Entradas"]], on="Período", how="left")
    merged = merged.merge(df_q1_filtered[["Período", "Tempo Médio (s)"]], on="Período", how="left", suffixes=("", "_Caixa1"))
    merged = merged.merge(df_q2_filtered[["Período", "Tempo Médio (s)"]], on="Período", how="left", suffixes=("", "_Caixa2"))

    merged.rename(columns={
        "Tempo Médio (s)": "Fila Caixa 1 (s)",
        "Tempo Médio (s)_Caixa2": "Fila Caixa 2 (s)"
    }, inplace=True)

    # Mapeia o horário
    merged["Horário"] = merged["Período"].map(period_to_time)
    merged.fillna(0, inplace=True)

    # Calcula totais do dia
    total_entradas = int(merged["Entradas"].sum())
    media_fila1 = round(merged["Fila Caixa 1 (s)"].mean(), 2)
    media_fila2 = round(merged["Fila Caixa 2 (s)"].mean(), 2)

    # Criação do PDF
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Cabeçalho
    story.append(Paragraph(f"<b>📄 Relatório de Entradas e Tempos de Fila — {date_str}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Resumo geral
    story.append(Paragraph("<b>📊 Resumo do Dia</b>", styles["Heading2"]))
    resumo_data = [
        ["Indicador", "Valor"],
        ["Total de Entradas", f"{total_entradas}"],
        ["Tempo Médio de Fila — Caixa 1 (s)", f"{media_fila1}"],
        ["Tempo Médio de Fila — Caixa 2 (s)", f"{media_fila2}"]
    ]

    resumo_table = Table(resumo_data, colWidths=[9*cm, 6*cm])
    resumo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(resumo_table)
    story.append(Spacer(1, 18))

    # Tabela detalhada
    story.append(Paragraph("<b>📅 Detalhamento por Período</b>", styles["Heading2"]))

    table_data = [["Horário", "Entradas", "Fila Caixa 1 (s)", "Fila Caixa 2 (s)"]]
    for _, row in merged.iterrows():
        table_data.append([
            row["Horário"],
            int(row["Entradas"]),
            round(row["Fila Caixa 1 (s)"], 2),
            round(row["Fila Caixa 2 (s)"], 2)
        ])

    table = Table(table_data, colWidths=[4.5*cm, 3.5*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
    ]))
    story.append(table)

    # Rodapé
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "<i>Relatório gerado automaticamente pelo Dashboard SmartAware.</i>",
        styles["Normal"]
    ))

    doc.build(story)
    return output_path
