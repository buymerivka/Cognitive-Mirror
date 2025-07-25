import os

import gdown
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def ensure_model():
    file_id = os.getenv('MODEL_ID')
    output_path = f'{BASE_DIR}/models/bert-goemotions/pytorch_model.bin'
    if not os.path.exists(output_path):
        gdown.download(f'https://drive.google.com/uc?id={file_id}', output_path, quiet=False)
        print('Model downloaded.')
    else:
        print('Model exists.')
