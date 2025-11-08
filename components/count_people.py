import pandas as pd
import os
import csv

BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

def get_people_count(camera_name, date_str, period):
    """Retorna o número de pessoas detectadas em um ambiente específico por período."""
    csv_path = os.path.join(BASE_DIR, camera_name, date_str, "count", "people_count.csv")
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path, sep=",")
    df.columns = df.columns.str.strip()
    period_str = str(period)

    for _, row in df.iterrows():
        if str(row["Período"]) == period_str:
            return row["Número de Pessoas"]
    return None

def get_total_people_count(camera_name: str, date_str: str):
    """Retorna o total de pessoas ('Total') do CSV do ambiente."""
    csv_path = os.path.join(BASE_DIR, camera_name, date_str, "count", "people_count.csv")
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Período"].strip().lower() == "total":
                return row["Número de Pessoas"]
    return None

def get_total_entries(date_str: str, period: int | None = None):
    """Retorna o total de pessoas que entraram na loja (camera11) — por período ou total diário."""
    csv_path = os.path.join(BASE_DIR, "camera11", date_str, "count", "people_total.csv")
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if period is None:
        total_row = df[df["Período"].str.lower() == "total"]
        if not total_row.empty:
            return int(total_row["Entradas"].values[0])
    else:
        period_str = str(period)
        row = df[df["Período"].astype(str) == period_str]
        if not row.empty:
            return int(row["Entradas"].values[0])

    return None
