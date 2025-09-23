import os

import gdown
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# MODEL_ID = os.getenv('PROPAGANDA_MODEL_ID')
# OPTIMIZER_ID = os.getenv('PROPAGANDA_OPTIMIZER_ID')
MODEL_ID = '14nlVdJTivuvkG9sVyy6SJhWnB7GGWflf'
OPTIMIZER_ID = '1-hHqCmrC7__m4FrFT3dMR9oMcMRg9QWQ'


def ensure_model():
    model_output_path = f'{BASE_DIR}/models/propaganda_bert_model_3.0/model.safetensors'
    if not os.path.exists(model_output_path):
        gdown.download(f'https://drive.google.com/uc?id={MODEL_ID}', model_output_path, quiet=False)
        print('Propaganda model downloaded.')
    else:
        print('Propaganda model exists.')

    optimizer_output_path = f'{BASE_DIR}/models/propaganda_bert_model_3.0/optimizer.pt'
    if not os.path.exists(optimizer_output_path):
        gdown.download(f'https://drive.google.com/uc?id={OPTIMIZER_ID}', optimizer_output_path, quiet=False)
        print('Propaganda optimizer downloaded.')
    else:
        print('Propaganda optimizer exists.')
