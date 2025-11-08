import pandas as pd
import plotly.express as px
import os
import streamlit as st
from datetime import datetime, date, timedelta

BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

# --- Mapeamento de períodos para horários ---
period_to_time = {
    1: "08:00 – 09:00", 2: "09:00 – 10:00", 3: "10:00 – 11:00",
    4: "11:00 – 12:00", 5: "12:00 – 13:00", 6: "13:00 – 14:00",
    7: "14:00 – 15:00", 8: "15:00 – 16:00", 9: "16:00 – 17:00",
    10: "17:00 – 18:00", 11: "18:00 – 19:00", 12: "19:00 – 20:00"
}


def show_people_chart(camera_name: str, date_str: str, placeholder):
    """Mostra o gráfico de fluxo de pessoas do ambiente."""
    csv_path = os.path.join(BASE_DIR, camera_name, date_str, "count", "people_count.csv")
    if not os.path.exists(csv_path):
        placeholder.error(f"Arquivo CSV não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df_plot = df[df["Período"].str.lower() != "total"].copy()
    df_plot["Período"] = df_plot["Período"].astype(int)
    df_plot["Horário"] = df_plot["Período"].map(period_to_time)

    fig = px.bar(
        df_plot,
        x="Horário",
        y="Número de Pessoas",
        title=f"Fluxo de Pessoas - {camera_name} ({date_str})",
        color="Número de Pessoas",
        color_continuous_scale="Blues",
        text="Número de Pessoas"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Horário",
        yaxis_title="Número de Pessoas",
        title_x=0.5,
        margin=dict(t=120)
    )
    placeholder.plotly_chart(fig, use_container_width=True)
    placeholder.info("Cada barra representa o número de pessoas detectadas em cada período do dia.")


def show_total_entries_chart(date_str: str, placeholder):
    """Mostra o gráfico de entradas totais da loja (camera11)."""
    csv_path = os.path.join(BASE_DIR, "camera11", date_str, "count", "people_total.csv")
    if not os.path.exists(csv_path):
        placeholder.error(f"Arquivo CSV não encontrado: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df_plot = df[df["Período"].str.lower() != "total"].copy()
    df_plot["Período"] = df_plot["Período"].astype(int)
    df_plot["Horário"] = df_plot["Período"].map(period_to_time)

    fig = px.bar(
        df_plot,
        x="Horário",
        y="Entradas",
        title=f"Total de Pessoas que Entraram na Loja ({date_str})",
        color="Entradas",
        color_continuous_scale="Greens",
        text="Entradas"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Horário",
        yaxis_title="Número de Entradas",
        title_x=0.5,
        margin=dict(t=120)
    )
    placeholder.plotly_chart(fig, use_container_width=True)
    placeholder.info("Cada barra representa o total de pessoas que entraram no estabelecimento em cada período.")


def show_queue_time_chart(date_str: str, placeholder):
    """Mostra o gráfico comparativo do tempo médio de fila (s) entre Caixa 1 e Caixa 2."""
    queue_dir = os.path.join(BASE_DIR, "camera11", date_str, "queue")
    queue_files = ["queue_time1.csv", "queue_time2.csv"]
    dfs = []

    for idx, file in enumerate(queue_files, start=1):
        csv_path = os.path.join(queue_dir, file)
        if not os.path.exists(csv_path):
            placeholder.warning(f"⚠️ Arquivo não encontrado: {file}")
            continue

        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        # Garante que as colunas existam
        if "Período" not in df.columns or "Tempo Médio (s)" not in df.columns:
            placeholder.warning(f"⚠️ Colunas esperadas não encontradas em {file}")
            continue

        # Converte para string apenas se possível
        df["Período"] = df["Período"].astype(str)

        # Remove linhas com 'total' de forma segura (independente do tipo)
        df = df[~df["Período"].apply(lambda x: isinstance(x, str) and x.lower() == "total")].copy()

        # Agora converte os períodos válidos em inteiros
        df["Período"] = pd.to_numeric(df["Período"], errors="coerce")
        df.dropna(subset=["Período"], inplace=True)
        df["Período"] = df["Período"].astype(int)

        # Mapeia horários
        df["Horário"] = df["Período"].map(period_to_time)
        df["Caixa"] = f"Caixa {idx}"

        # Mantém apenas colunas necessárias
        df = df[["Horário", "Tempo Médio (s)", "Caixa"]]
        dfs.append(df)

    # Caso nenhum DataFrame tenha sido carregado corretamente
    if not dfs:
        placeholder.error("Nenhum arquivo de tempo de fila encontrado ou em formato incorreto.")
        return

    # Junta os dois arquivos
    df_final = pd.concat(dfs, ignore_index=True)

    # Cria o gráfico
    fig = px.bar(
        df_final,
        x="Horário",
        y="Tempo Médio (s)",
        color="Caixa",
        barmode="group",
        text="Tempo Médio (s)",
        color_discrete_map={"Caixa 1": "#007bff", "Caixa 2": "#28a745"},
        title=f"Tempo Médio de Fila ({date_str})"
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis_title="Horário",
        yaxis_title="Tempo Médio (s)",
        title_x=0.5,
        legend_title_text="",
        margin=dict(t=120)
    )
    placeholder.plotly_chart(fig, use_container_width=True)
    placeholder.info("Cada barra mostra o tempo médio de fila (em segundos) para cada caixa durante o dia.")

# --- gráfico de entradas por dia na semana selecionada ---
def show_total_entries_last_15_days_chart(selected_date_str: str, placeholder):
    """
    Mostra o total de pessoas que entraram na loja (camera11)
    na data selecionada e nos 15 dias anteriores.
    Se não houver CSV em algum dia, mostra 0.
    """
    try:
        sel_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except Exception:
        placeholder.error(f"Data inválida: {selected_date_str}")
        return

    # Gera o intervalo de 15 dias anteriores + data selecionada
    date_range = [sel_date - timedelta(days=i) for i in range(15, -1, -1)]

    data_rows = []
    for d in date_range:
        d_str = d.strftime("%Y-%m-%d")
        csv_path = os.path.join(BASE_DIR, "camera11", d_str, "count", "people_total.csv")

        total_value = 0
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()
                if "Período" in df.columns:
                    period_col = df["Período"].astype(str).str.strip().str.lower()
                    total_row = df[period_col.eq("total")]
                    if not total_row.empty:
                        if "Entradas" in total_row.columns:
                            total_value = pd.to_numeric(total_row["Entradas"].iloc[0], errors="coerce")
                        elif "Número de Pessoas" in total_row.columns:
                            total_value = pd.to_numeric(total_row["Número de Pessoas"].iloc[0], errors="coerce")
                        total_value = 0 if pd.isna(total_value) else int(total_value)
            except Exception:
                total_value = 0

        data_rows.append({"Data": d_str, "Total de Entradas": total_value})

    # Converte Data → datetime e formata para o eixo
    df_plot = pd.DataFrame(data_rows)
    df_plot["Data"] = pd.to_datetime(df_plot["Data"], errors="coerce")
    df_plot["Dia"] = df_plot["Data"].dt.strftime("%d/%m")

    # Gráfico de linha
    fig = px.line(
        df_plot,
        x="Dia",
        y="Total de Entradas",
        markers=True,
        title=f"📆 Entradas Diárias — Últimos 15 dias até {sel_date.strftime('%d/%m/%Y')}",
        color_discrete_sequence=["#2ca02c"]
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Total de Entradas",
        title_x=0.5,
        margin=dict(t=90)
    )
    placeholder.plotly_chart(fig, use_container_width=True)
    placeholder.info("Dias sem dados aparecem com valor 0.")
