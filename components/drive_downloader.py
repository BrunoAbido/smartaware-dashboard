import os
import gdown
import streamlit as st

FILE_MAP = {
    "camera11": {
        "2025-10-07": {
            "heatmap": "1i8xSsLJA-4Lrofnr7-aAfo59jfL1Wj5i",
            "count": "1ViM077TnVXlsVujO57Iui-GANW7BfdOu",
            "queue": "1IGjbE7weEOnX2ulpq3Jpcnj68sFHOHiS",
        },
    },
}

@st.cache_data(show_spinner=False)
def download_drive_file(file_id: str, output_path: str):
    """Baixa um arquivo do Google Drive se ele ainda não existir localmente."""
    if os.path.exists(output_path):
        return output_path

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)
    return output_path


def ensure_data_for_selection(camera_name: str, date_str: str):
    """
    Garante que os arquivos da câmera e data selecionadas existam localmente.
    Baixa apenas os necessários (heatmap, count, queue) se não existirem.
    """
    if camera_name not in FILE_MAP or date_str not in FILE_MAP[camera_name]:
        st.warning(f"Nenhum arquivo configurado para {camera_name} - {date_str}.")
        return

    base_dir = os.path.join("data", "detections", camera_name, date_str)
    mapping = FILE_MAP[camera_name][date_str]

    for key, file_id in mapping.items():
        if key == "heatmap":
            output_path = os.path.join(base_dir, "heatmaps", "heatmap_interval_1.png")
        elif key == "count":
            output_path = os.path.join(base_dir, "count", "people_total.csv")
        elif key == "queue":
            output_path = os.path.join(base_dir, "queue", "queue_time1.csv")
        else:
            continue

        download_drive_file(file_id, output_path)
