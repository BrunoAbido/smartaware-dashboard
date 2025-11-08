import pandas as pd
import os

BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

def get_queue_time(date_str: str, queue_number: int, period: int | None = None):
    """
    Retorna o tempo médio de fila (em segundos) de um caixa específico.
    Se 'period' for None, retorna a média geral do dia.
    """
    csv_path = os.path.join(BASE_DIR, "camera11", date_str, "queue", f"queue_time{queue_number}.csv")
    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # Garante tipos numéricos
    if "Tempo Médio (s)" not in df.columns or "Período" not in df.columns:
        return None

    # Força conversão numérica (ignora strings e NaN)
    df["Tempo Médio (s)"] = pd.to_numeric(df["Tempo Médio (s)"], errors="coerce")

    if period is None:
        media = df["Tempo Médio (s)"].mean(skipna=True)
        return round(float(media), 2) if not pd.isna(media) else None
    else:
        row = df.loc[df["Período"] == period, "Tempo Médio (s)"]
        if not row.empty:
            valor = row.iloc[0]
            if pd.notna(valor):
                return round(float(valor), 2)
    return None


def get_queue_times(date_str: str, period: int | None = None):
    """
    Retorna os tempos médios de fila dos dois caixas (1 e 2).
    Retorna uma tupla (caixa1, caixa2).
    """
    caixa1 = get_queue_time(date_str, 1, period)
    caixa2 = get_queue_time(date_str, 2, period)
    return caixa1, caixa2
