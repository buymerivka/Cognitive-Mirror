import os

from dotenv import load_dotenv
from fastapi import Request
from nicegui import ui
from views import (
    render_analyze_emotions_request,
    render_analyze_manipulations_request,
    render_analyze_request,
    render_error,
)

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')


@ui.page('/')
def base_page():
    ui.navigate.to('/analyze')


@ui.page('/analyze_manipulations')
def analyze_manipulations_request(request: Request):
    render_analyze_manipulations_request()


@ui.page('/analyze_emotions')
def analyze_emotions_request(request: Request):
    render_analyze_emotions_request()


@ui.page('/analyze')
def analyze_request(request: Request):
    render_analyze_request()


@ui.page('/error')
def error(request: Request):
    render_error()


ui.run(title='Cognitive-Mirror', port=8080)
