# src/dashboard/components/heatmaps.py
import os
from PIL import Image
import streamlit as st

BASE_DIR = r"G:\Meu Drive\Colab Notebooks\data\detections"

def get_heatmap_file(camera_name: str, date_str: str, interval_number):
    """Retorna o caminho completo do arquivo de heatmap para a câmera, data e intervalo."""
    if interval_number == "total":
        return os.path.join(BASE_DIR, camera_name, date_str, "heatmaps", "heatmap_total.png")
    else:
        return os.path.join(BASE_DIR, camera_name, date_str, "heatmaps", f"heatmap_interval_{interval_number}.png")

def load_heatmap(camera_name: str, date_str: str, interval_number: int):
    heatmap_file = get_heatmap_file(camera_name, date_str, interval_number)
    if os.path.exists(heatmap_file):
        return Image.open(heatmap_file)
    return None

def display_heatmap(camera_name: str, date_str: str, interval_number: int):
    img = load_heatmap(camera_name, date_str, interval_number)
    if img:
        st.image(img, caption=f"📍 {camera_name} | {date_str} | Intervalo {interval_number}", use_container_width=True)
    else:
        st.warning("⚠️ Heatmap não encontrado para os filtros selecionados.")

def get_available_cameras():
    """Retorna as câmeras disponíveis dentro de data/detections."""
    if not os.path.exists(BASE_DIR):
        return []
    return sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])

def get_available_dates(camera_name: str):
    """Retorna as datas disponíveis para uma câmera."""
    camera_path = os.path.join(BASE_DIR, camera_name)
    if not os.path.exists(camera_path):
        return []
    return sorted([d for d in os.listdir(camera_path) if os.path.isdir(os.path.join(camera_path, d))])

def get_intervals(camera_name: str, date_str: str):
    """Retorna os intervalos disponíveis dentro da pasta heatmaps da data escolhida."""
    heatmaps_path = os.path.join(BASE_DIR, camera_name, date_str, "heatmaps")
    if not os.path.exists(heatmaps_path):
        return []
    heatmap_files = [f for f in os.listdir(heatmaps_path) if f.startswith("heatmap_interval_")]
    intervals_available = sorted(set(int(f.split("_")[-1].split(".")[0]) for f in heatmap_files))
    return intervals_available

def heatmap_filter_ui():
    """Interface Streamlit para escolher câmera, data e intervalo."""
    st.sidebar.header("🎛️ Filtros de Heatmap")

    cameras = get_available_cameras()
    camera_name = st.sidebar.selectbox("📷 Câmera", cameras) if cameras else None

    dates = get_available_dates(camera_name) if camera_name else []
    date_str = st.sidebar.selectbox("📅 Data", dates) if dates else None

    intervals = get_intervals(camera_name, date_str) if camera_name and date_str else []
    interval_number = st.sidebar.selectbox("⏱️ Período (1–12)", intervals) if intervals else None

    if camera_name and date_str and interval_number:
        display_heatmap(camera_name, date_str, interval_number)
    else:
        st.info("Selecione uma câmera, data e período para visualizar o heatmap.")
