# components/utils.py

def format_camera_name(camera_name: str) -> str:

    mapping = {
        "camera11": "ENTRADA",
        # "camera12": "Corredor Principal",
        # "camera13": "Caixa 1",
    }

    return mapping.get(camera_name, camera_name.capitalize())
