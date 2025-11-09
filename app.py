import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from components.heatmaps import display_heatmap, get_available_cameras, get_available_dates, get_intervals
from components.count_people import get_people_count, get_total_people_count, get_total_entries
from components.queue_time import get_queue_times
from components.graficos import show_queue_time_chart
from components.utils import format_camera_name
from components.graficos import show_total_entries_last_15_days_chart
from components.export_pdf import generate_daily_report
from streamlit_scroll_to_top import scroll_to_here  # scroll automático

from components.drive_loader import download_drive_folder

BASE_DIR = "data/detections"

# Baixar dados do Drive (somente se a pasta local não existir)
if not os.path.exists(BASE_DIR):
    download_drive_folder("https://drive.google.com/drive/folders/1tOUMDs-SdgF1X9q-d2okdmHtn1iYLRBo?usp=sharing", BASE_DIR)


BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

# --- Configuração da página ---
st.set_page_config(page_title="Mapa de Calor - Circulação", layout="wide")
st.title("Circulação no Estabelecimento")

# --- Ajuste de margens e espaçamento ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 2.8rem !important;
        padding-bottom: 1rem !important;
    }
    header, [data-testid="stHeader"] {
        margin-top: 0.5rem !important;
        padding-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Estado de sessão ---
if "show_people_chart" not in st.session_state:
    st.session_state.show_people_chart = False
if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False

def scroll_bottom():
    st.session_state.scroll_to_bottom = True

# --- FILTROS ---
st.sidebar.header("🎛️ Filtros")
cameras = get_available_cameras()

# 🔹 Garante que 'camera11' (Entrada) venha primeiro e 'camera10' por último
if "camera11" in cameras:
    cameras.remove("camera11")
    cameras.insert(0, "camera11")

if "camera10" in cameras:
    cameras.remove("camera10")
    cameras.append("camera10")

# 🔹 Mapeia nomes técnicos para nomes amigáveis
camera_labels = [format_camera_name(cam) for cam in cameras]

# 🔹 Cria o selectbox mostrando o nome amigável, mas retornando o código real
selected_label = st.sidebar.selectbox(
    "📷 Selecionar Câmera",
    camera_labels,
    key="camera_selectbox"
) if cameras else None

selected_camera = cameras[camera_labels.index(selected_label)] if selected_label else None

# --- Datas disponíveis ---
dates_str = get_available_dates(selected_camera) if selected_camera else []
dates_available = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates_str]

if dates_available:
    min_date = min(dates_available)
    max_date = max(dates_available)
    selected_date = st.sidebar.date_input(
        "📅 Selecionar Data", value=min_date, min_value=min_date, max_value=max_date
    )
    if selected_date not in dates_available:
        st.sidebar.warning("⚠️ Nenhum Mapa de Calor disponível nesta data.")
        selected_date = None
else:
    selected_date = None

# --- Intervalos (períodos de tempo) ---
intervals = get_intervals(selected_camera, selected_date.strftime("%Y-%m-%d")) if selected_camera and selected_date else []

period_to_time = {
    1: "08:00 – 09:00", 2: "09:00 – 10:00", 3: "10:00 – 11:00",
    4: "11:00 – 12:00", 5: "12:00 – 13:00", 6: "13:00 – 14:00",
    7: "14:00 – 15:00", 8: "15:00 – 16:00", 9: "16:00 – 17:00",
    10: "17:00 – 18:00", 11: "18:00 – 19:00", 12: "19:00 – 20:00"
}

# 🔹 Cria o selectbox de horário
labels = ["📆 Dia inteiro"]
values = [None]
for p in intervals:
    labels.append(period_to_time.get(p, f"Período {p}"))
    values.append(p)

selected_interval_label = st.sidebar.selectbox(
    "⏱️ Selecionar Horário",
    labels,
    key="interval_selectbox"
)
selected_interval = values[labels.index(selected_interval_label)]
is_full_day = selected_interval is None

# --- Botão para gerar relatório (agora logo abaixo dos filtros principais) ---
st.sidebar.markdown("### 📄 Relatório Diário")
if selected_date:
    date_str = selected_date.strftime("%Y-%m-%d")
    if st.sidebar.button("📊 Gerar Relatório do Dia"):
        try:
            output_path = generate_daily_report(date_str)
            st.sidebar.success("✅ Relatório gerado com sucesso!")
            with open(output_path, "rb") as f:
                st.sidebar.download_button(
                    label="⬇️ Baixar Relatório PDF",
                    data=f,
                    file_name=f"relatorio_{date_str}.pdf",
                    mime="application/pdf"
                )
        except FileNotFoundError:
            st.sidebar.error("⚠️ Arquivos necessários não encontrados para essa data.")
        except Exception as e:
            st.sidebar.error(f"❌ Erro ao gerar relatório: {e}")
else:
    st.sidebar.info("Selecione uma data para gerar o relatório.")



# --- Layout ---
left_col, right_col = st.columns([6, 3])

with left_col:
    if selected_camera and selected_date:
        date_str = selected_date.strftime("%Y-%m-%d")
        if is_full_day:
            st.subheader(f"{format_camera_name(selected_camera)} - {date_str} - Dia inteiro")

            display_heatmap(selected_camera, date_str, "total")
        else:
            st.subheader(f"{format_camera_name(selected_camera)} - {date_str} - Horário {selected_interval_label}")
            display_heatmap(selected_camera, date_str, selected_interval)

        # --- Botão "Ver mais" abaixo do Heatmap ---
        st.markdown("""
        <style>
        div.stButton {
            display: flex;
            justify-content: center;
            margin-top: 4px;      /* distância menor entre mapa e botão */
            margin-bottom: 0;
        }
        div.stButton > button {
            background-color: #6c757d;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px 60px;
            border: 1.5px solid #bfbfbf;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: all 0.25s ease;
            margin: 0 auto;
        }
        div.stButton > button:hover {
            background-color: #5a6268;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.18);
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("Ver mais", key="ver_mais_heatmap"):
            st.session_state.show_people_chart = True
            scroll_bottom()
            st.rerun()
    else:
        st.info("Selecione uma câmera, data e período para visualizar o heatmap.")


        

with right_col:
    if selected_date:
        date_str = selected_date.strftime("%Y-%m-%d")
        st.subheader(f"📊 Informações Gerais do dia {date_str}")

        # --- Período ---
        period_text = "Dia inteiro" if is_full_day else selected_interval_label
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="font-size: 18px; font-weight: 500;">🕓 Período</div>
                <div style="
                    background-color:#f5f5f5;
                    padding:1px;
                    border-radius:8px;
                    text-align:center;
                    font-size:20px;
                    font-weight:bold;
                    color:#333;
                    border:1px solid #ccc;
                    width:150px;">
                    {period_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Número de pessoas no ambiente ---
        people_count = None
        if selected_camera:
            if is_full_day:
                people_count = get_total_people_count(selected_camera, date_str)
            else:
                people_count = get_people_count(selected_camera, date_str, selected_interval)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="font-size: 18px; font-weight: 500;">📊 Número de Pessoas no ambiente</div>
                <div style="
                    background-color:#f5f5f5;
                    padding:2px;
                    border-radius:8px;
                    text-align:center;
                    font-size:28px;
                    font-weight:bold;
                    color:#333;
                    border:1px solid #ccc;
                    width:80px;
                    flex-shrink:0;">
                    {people_count if people_count is not None else '–'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Total de pessoas que entraram na loja ---
        total_entries = None
        if is_full_day:
            total_entries = get_total_entries(date_str)
        else:
            total_entries = get_total_entries(date_str, selected_interval)

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                <div style="font-size: 18px; font-weight: 500;">
                    🚶‍♂️ Número de Pessoas que entraram na loja
                </div>
                <div style="
                    background-color:#f5f5f5;
                    padding:2px;
                    border-radius:8px;
                    text-align:center;
                    font-size:28px;
                    font-weight:bold;
                    color:#333;
                    border:1px solid #ccc;
                    width:80px;
                    flex-shrink:0;">
                    {total_entries if total_entries is not None else '–'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Tempo médio de fila por caixas ---
        caixa1, caixa2 = get_queue_times(date_str, None if is_full_day else selected_interval)
        import math
        def fmt(v):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return "–"
            return f"{float(v):.2f}"

        v1, v2 = fmt(caixa1), fmt(caixa2)

        st.markdown('<div style="font-size: 18px; font-weight: 500; margin-bottom: 10px;">🕒 Tempo médio de fila por caixas (segundos)</div>', unsafe_allow_html=True)

        for i, val in enumerate([v1, v2], start=1):
            st.markdown(f'''
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <div style="font-size: 18px; font-weight: 500;">Caixa {i}</div>
                <div style="
                    background-color:#f5f5f5;
                    padding:2px;
                    border-radius:8px;
                    text-align:center;
                    font-size:22px;
                    font-weight:bold;
                    color:#333;
                    border:1px solid #ccc;
                    width:80px;">
                    {val}
                </div>
            </div>
            ''', unsafe_allow_html=True)


# --- Gráficos ---
if selected_camera and selected_date and st.session_state.show_people_chart:
    date_str = selected_date.strftime("%Y-%m-%d")

    # === Gráfico 1: Pessoas no ambiente selecionado ===
    csv_path = os.path.join(BASE_DIR, selected_camera, date_str, "count", "people_count.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        df_plot = df[df["Período"].str.lower() != "total"]
        df_plot["Período"] = df_plot["Período"].apply(lambda x: period_to_time.get(int(x), x))

        st.subheader("📈 Fluxo de Pessoas no Ambiente Selecionado")
        fig1 = px.bar(
            df_plot,
            x="Período",
            y="Número de Pessoas",
            color="Número de Pessoas",
            color_continuous_scale="Blues",
            text="Número de Pessoas",
            title=f"Fluxo de Pessoas - {selected_camera} ({date_str})"
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(xaxis_title="Horário", yaxis_title="Número de Pessoas", title_x=0.5, margin=dict(t=70))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.error("Arquivo people_count.csv não encontrado.")

    # === Gráfico 2: Total de Pessoas que Entraram no Estabelecimento ===
    total_csv_path = os.path.join(BASE_DIR, "camera11", date_str, "count", "people_total.csv")
    if os.path.exists(total_csv_path):
        df_total = pd.read_csv(total_csv_path)
        df_total.columns = df_total.columns.str.strip()
        df_total_plot = df_total[df_total["Período"].str.lower() != "total"]
        df_total_plot["Período"] = df_total_plot["Período"].apply(lambda x: period_to_time.get(int(x), x))

        st.subheader("📊 Total de Pessoas que Entraram no Estabelecimento")
        fig2 = px.bar(
            df_total_plot,
            x="Período",
            y="Entradas",
            color="Entradas",
            color_continuous_scale="Greens",
            text="Entradas",
            title=f"Entradas no Estabelecimento ({date_str})"
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(xaxis_title="Horário", yaxis_title="Número de Entradas", title_x=0.5, margin=dict(t=90))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Arquivo people_total.csv não encontrado.")

    # === Gráfico 3: Tempo Médio de Fila por Caixa ===
    st.subheader("🕒 Comparativo de Tempo Médio de Fila por Caixa")
    show_queue_time_chart(date_str, st)


    # === Gráfico 4: Entradas por Dia (últimos 15 dias) ===
    st.subheader("📅 Evolução de Entradas nos Últimos 15 Dias")
    show_total_entries_last_15_days_chart(date_str, st)



    # --- Scroll automático ---
    if st.session_state.scroll_to_bottom:
        scroll_to_here(0, key="bottom")
        st.session_state.scroll_to_bottom = False
