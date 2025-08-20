import json
import os

import requests
from dotenv import load_dotenv
from nicegui import ui

load_dotenv()
API_BASE_URL: str = os.getenv('API_BASE_URL')


def create_request_propaganda(request_text: str, top_n: int = 1):
    api_response = requests.post(f'{API_BASE_URL}/analyze_propaganda?top_n={top_n}',
                                 json={'input_data': request_text})

    if api_response.status_code == 200:
        return api_response.json()['analyzed_data']
    return None


def create_request_emotions(request_text: str, top_n: int = 1):
    api_response = requests.post(f'{API_BASE_URL}/analyze_emotions?top_n={top_n}',
                                 json={'input_data': request_text})

    if api_response.status_code == 200:
        return api_response.json()['analyzed_data']
    return None


def create_request(request_text: str, top_n_propaganda: int = 1, top_n_emotions: int = 1):
    api_response = requests.post(f'{API_BASE_URL}/analyze?'
                                 f'top_n_propaganda={top_n_propaganda}&top_n_emotions={top_n_emotions}',
                                 json={'input_data': request_text})

    if api_response.status_code == 200:
        return api_response.json()
    return None


def download_json(json_data):
    js_code = f'''
    const blob = await fetch('{API_BASE_URL}/download-json', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json'
        }},
        body: JSON.stringify({json.dumps(json_data)})
    }}).then(r => r.blob());

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "analyzed_data.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    '''

    ui.run_javascript(js_code)
