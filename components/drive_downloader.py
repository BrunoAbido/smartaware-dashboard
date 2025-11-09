import os
import gdown

BASE_DIR = "data/detections"

# 🔹 IDs públicos do Google Drive de cada câmera (substitua pelos seus)
DRIVE_CAMERA_IDS = {
    "camera11": "1xXWb5wY2C6AdPbA7UwLPCg4pDo27RQpK",  # Entrada
    "camera1": "1IvwZP7CUkq1p2QeUThjQk7gV4WqDWapJ",
    "camera2": "1mjPOJPN5QtA13aThL2IrZzDkZebkVRQm",
    "camera10": "1x7b5y-MlfB-F1VVVYH8hM6P1MB9TxExU",
}


def ensure_camera_data(camera_name: str, date_str: str):
    """
    Baixa apenas os arquivos necessários da câmera e data selecionadas.
    Ignora arquivos grandes (npy, vídeos, etc.).
    """
    if camera_name not in DRIVE_CAMERA_IDS:
        print(f"⚠️ Câmera {camera_name} não possui ID configurado.")
        return

    target_dir = os.path.join(BASE_DIR, camera_name, date_str)
    os.makedirs(target_dir, exist_ok=True)

    # Evita baixar novamente se já existe algo útil
    if any(fname.endswith((".png", ".csv")) for fname in os.listdir(target_dir)):
        print(f"✅ Dados já disponíveis para {camera_name}/{date_str}")
        return

    print(f"📥 Baixando dados de {camera_name}/{date_str}...")

    # 🔹 Caminho base da pasta da câmera no Google Drive
    camera_folder_id = DRIVE_CAMERA_IDS[camera_name]
    camera_folder_url = f"https://drive.google.com/drive/folders/{camera_folder_id}"

    # 🔹 Baixa todos os arquivos da pasta da câmera (mas filtrando manualmente)
    files = gdown.download_folder(
        url=camera_folder_url,
        quiet=False,
        use_cookies=False,
        remaining_ok=True
    )

    if not files:
        print("⚠️ Nenhum arquivo encontrado no Drive.")
        return

    # 🔹 Filtra apenas os arquivos necessários
    for file_path in files:
        file_name = os.path.basename(file_path)
        if file_name.endswith((".png", ".csv")):
            dest_path = os.path.join(target_dir, file_name)
            os.rename(file_path, dest_path)
            print(f"✅ Mantido: {file_name}")
        else:
            os.remove(file_path)
            print(f"🗑️ Ignorado: {file_name}")

    print(f"✅ Dados prontos para {camera_name}/{date_str} em {target_dir}")
