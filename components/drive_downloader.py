import os
import gdown
import streamlit as st

BASE_DIR = "data/detections"

# 🔹 Pasta raiz pública do Google Drive (detections/)
DRIVE_BASE_URL = "https://drive.google.com/drive/folders/1tOUMDs-SdgF1X9q-d2okdmHtn1iYLRBo?usp=sharing"

def ensure_camera_data(camera_name: str, date_str: str):
    """
    Baixa apenas os arquivos necessários da câmera e data selecionadas.
    Ignora arquivos grandes (npy, vídeos, etc.).
    """
    target_dir = os.path.join(BASE_DIR, camera_name, date_str)
    os.makedirs(target_dir, exist_ok=True)

    # Evita baixar novamente se já existe algo útil
    if any(fname.endswith((".png", ".csv")) for fname in os.listdir(target_dir)):
        print(f"✅ Dados já disponíveis para {camera_name}/{date_str}")
        return

    st.sidebar.info(f"⏳ Baixando dados de {camera_name} ({date_str}) do Google Drive...")

    try:
        # 🔹 Tenta baixar a subpasta correspondente
        folder_url = f"{DRIVE_BASE_URL}/{camera_name}/{date_str}"
        files = gdown.download_folder(
            url=folder_url,
            quiet=False,
            use_cookies=False,
            remaining_ok=True
        )

        if not files:
            st.sidebar.warning(f"⚠️ Nenhum arquivo encontrado para {camera_name}/{date_str}.")
            return

        for file_path in files:
            file_name = os.path.basename(file_path)
            if file_name.endswith((".png", ".csv")):
                dest_path = os.path.join(target_dir, file_name)
                os.replace(file_path, dest_path)
            else:
                os.remove(file_path)

        st.sidebar.success(f"✅ Dados prontos para {camera_name}/{date_str}")
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao baixar dados: {e}")
