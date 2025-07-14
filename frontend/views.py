import os

from dotenv import load_dotenv
from nicegui import ui

from services import create_request

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")


def render_header():
    with ui.header().classes(
            'w-full border-b-2 border-black py-0 px-0 items-center justify-center fixed-top bg-white').props(
        'id="header_log_in"'):
        with ui.column().classes('items-center '):
            ui.label('Cognitive-Mirror').classes('text-[40px] text-black')

        with ui.row().classes('absolute right-[15px] flex items-center'):
            ui.add_head_html('''
                <style>
                    .btn-outline-light-cst {
                        color: black !important;
                        background-color: transparent !important;
                        border: 1px solid black !important;
                        padding: 6px 12px !important;
                        border-radius: 8px !important;
                        transition: all 0.2s ease-in-out !important;
                        width: 100px !important;
                        text-decoration: none;
                        font-size: 14px;
                    }
                    .btn-outline-light-cst:hover {
                        color: white !important; /* dark text */
                        background-color: black !important;
                        text-decoration: none !important;
                    }
                </style>
            ''')


def render_footer():
    with ui.footer().classes(
            'w-full border-t-2 border-gray-300 justify-between items-start flex-wrap bg-white text-black absolute'):
        with ui.column().classes('gap-4 min-w-[250px]'):
            ui.label('Cognitive-Mirror').classes('text-[32px]')


def render_analyze_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        with ui.row().classes('w-[1000px] gap-0 justify-center'):
            ui.add_head_html('''
                <style>
                    .create-title {
                        resize: none;
                    }

                    .create-description {
                        resize: none;
                    }
                </style>
            ''')
            with ui.column().classes('gap-0'):
                ui.label('Provide a text').classes('text-[18px] mt-[20px] justify-center')
                description = ui.textarea().classes('w-[600px]').props('id=create-request outlined dense autogrow')

            def create_on_click():
                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                parsed_data = create_request(description.value)
                if not parsed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.card():
                            '''
                            'paragraphIndex': sentence_info.paragraphIndex,
                            'sentenceIndex': sentence_info.sentenceIndex,
                            'text': sentence_info.text,
                            'charStart': sentence_info.charStart,
                            'charEnd': sentence_info.charEnd
                            '''
                            for idx, data in enumerate(parsed_data):
                                if idx != len(parsed_data) - 1:
                                    with ui.column().classes('border-b-2 border-black p-[0px]'):
                                        ui.label(f'Paragraph Index: {data['paragraphIndex']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Sentence Index: {data['sentenceIndex']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Text: {data['text']}').classes('text-[18px] justify-center')
                                        ui.label(f'Char Start: {data['charStart']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Char End: {data['charEnd']}').classes(
                                            'text-[18px] justify-center pb-[16px]')
                                else:
                                    with ui.column().classes('border-black p-[0px]'):
                                        ui.label(f'Paragraph Index: {data['paragraphIndex']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Sentence Index: {data['sentenceIndex']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Text: {data['text']}').classes('text-[18px] justify-center')
                                        ui.label(f'Char Start: {data['charStart']}').classes(
                                            'text-[18px] justify-center')
                                        ui.label(f'Char End: {data['charEnd']}').classes(
                                            'text-[18px] justify-center pb-[16px]')
                            ui.button('Clear', color='#808080', on_click=lambda: card_container.clear()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                'self-end')

            card_container = ui.column().classes('mt-[20px]')

    render_footer()


def render_analyze_response(analyze_result):
    render_header()
    ui.label(analyze_result).classes('text-[32px] text-black text-bold')
    render_footer()


def render_error():
    render_header()
    ui.label('An error occurred').classes('text-[32px] text-black text-bold')
    render_footer()
