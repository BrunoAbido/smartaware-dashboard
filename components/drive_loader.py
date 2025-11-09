import gdown
import os

def download_drive_folder(folder_url, output_dir):
    """
    Baixa todos os arquivos de uma pasta pública do Google Drive para o diretório especificado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    gdown.download_folder(
        url=folder_url,
        output=output_dir,
        quiet=False,
        use_cookies=False
    )
    print("✅ Dados baixados com sucesso para:", output_dir)
