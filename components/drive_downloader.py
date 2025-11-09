import os
import gdown

BASE_DIR = "data/detections"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1tOUMDs-SdgF1X9q-d2okdmHtn1iYLRBo?usp=sharing"

def ensure_data_for_selection():
    """Baixa apenas a estrutura base se não houver câmeras locais."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    if not any(os.scandir(BASE_DIR)):
        print("📥 Nenhuma câmera local encontrada. Baixando estrutura básica...")
        gdown.download_folder(DRIVE_FOLDER_URL, output=BASE_DIR, quiet=False, use_cookies=False)
        print("✅ Estrutura base carregada.")
    else:
        print("✅ Estrutura já disponível.")
