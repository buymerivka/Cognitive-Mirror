import os

import gdown
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_ID = '1N2ZTApy4j92siOJBhm9cxpRylfA_EIac'
load_dotenv()


def ensure_model():
    output_path = f'{BASE_DIR}/models/bert-goemotions/pytorch_model.bin'
    if not os.path.exists(output_path):
        gdown.download(f'https://drive.google.com/uc?id={MODEL_ID}', output_path, quiet=False)
        print('Model downloaded.')
    else:
        print('Model exists.')
