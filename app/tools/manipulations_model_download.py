import os

import gdown
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# MODEL_ID = os.getenv('MANIPULATIONS_MODEL_ID')
# OPTIMIZER_ID = os.getenv('MANIPULATIONS_OPTIMIZER_ID')
MODEL_ID = '1IHfjtNfH_lqbDcr0C1pESNuu0qTDm5oG'
OPTIMIZER_ID = '1iu-C_t_sz1IiURSl4IXsoIpCrtaaMcIS'


def ensure_model():
    model_output_path = f'{BASE_DIR}/models/manipulations_bert_model/model.safetensors'
    if not os.path.exists(model_output_path):
        gdown.download(f'https://drive.google.com/uc?id={MODEL_ID}', model_output_path, quiet=False)
        print('Manipulations model downloaded.')
    else:
        print('Manipulations model exists.')

    optimizer_output_path = f'{BASE_DIR}/models/manipulations_bert_model/optimizer.pt'
    if not os.path.exists(optimizer_output_path):
        gdown.download(f'https://drive.google.com/uc?id={OPTIMIZER_ID}', optimizer_output_path, quiet=False)
        print('Manipulations optimizer downloaded.')
    else:
        print('Manipulations optimizer exists.')
