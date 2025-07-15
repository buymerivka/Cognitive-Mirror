import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL: str = os.getenv('API_BASE_URL')


def create_request(request_text: str):
    api_response = requests.post(f'{API_BASE_URL}/analyze',
                                 json={'input_data': request_text})

    if api_response.status_code == 200:
        return api_response.json()['parsed_data']
    return None
