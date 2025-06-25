import os
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

sheet_config = {
    "ETA Cubatão": {
        "SHEET_ID": os.getenv("ETA_CUBATAO_SHEET_ID"),
        "GID": os.getenv("ETA_CUBATAO_GID"),
    },
    "ETA Piraí": {
        "SHEET_ID": os.getenv("ETA_PIRAI_SHEET_ID"),
        "GID": os.getenv("ETA_PIRAI_GID"),
    },
}
