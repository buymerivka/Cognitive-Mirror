import os

from colors_tool import emotion_colors, propaganda_colors
from dotenv import load_dotenv
from nicegui import ui
from services import create_request, create_request_emotions, create_request_propaganda

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')


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


def render_analyze_propaganda_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.column().classes('mt-[20px] w-[1000px]')
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
                analyzed_data = create_request_propaganda(description.value, top_n.value)
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.card():
                            last_paragraph_id = 0
                            parts = []
                            for data in analyzed_data:
                                text = data['text']
                                predictions = data['predictions']
                                bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                tooltip_table = '<table style="font-size: 16px">'
                                tooltip_table += ('<p style="text-align: center; '
                                                  'font-weight: bold">Most likely propaganda techniques<p>')
                                for p in predictions:
                                    score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                    tooltip_table += (
                                        f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{p["label"]}</td>'
                                        f'<td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{score_to_display}</td></tr>'
                                    )
                                tooltip_table += '</table>'

                                span_html = f'''
                                <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
                                    {text}
                                    <span class="tooltiptext">{tooltip_table}</span>
                                </span>
                                '''
                                if last_paragraph_id != data['paragraphIndex']:
                                    span_html = '<br>' + span_html
                                    last_paragraph_id = data['paragraphIndex']
                                parts.append(span_html)

                            ui.add_head_html('''
                            <style>
                            .tooltip {
                                position: relative;
                                display: inline;
                                cursor: pointer;
                                white-space: normal;
                            }
                            .tooltip .tooltiptext {
                                visibility: hidden;
                                background-color: #f9f9f9;
                                color: #000;
                                text-align: left;
                                border-radius: 6px;
                                border: 1px solid #ccc;
                                padding: 6px;
                                position: absolute;
                                z-index: 9999;
                                top: 1.5em;
                                left: 0;
                                opacity: 0;
                                transition: opacity 0.2s;
                                white-space: nowrap;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                            }
                            .tooltip:hover .tooltiptext {
                                visibility: visible;
                                opacity: 1;
                            }
                            </style>
                            ''')

                            joined_html = ' '.join(parts)
                            ui.html(f'<div style="font-size: 18px; line-height: 1.6; '
                                    f'text-align: justify;">{joined_html}</div>')
                            ui.button('Clear', color='#808080', on_click=lambda: card_container.clear()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                top_n = ui.number(value=1).classes('self-center w-[180px]')
                top_n.min = 1
                top_n.max = len(propaganda_colors)
                top_n.label = '# of propaganda techniques'
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_emotions_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.column().classes('mt-[20px] w-[1000px]')
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
                analyzed_data = create_request_emotions(description.value, top_n.value)
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.card():
                            last_paragraph_id = 0
                            parts = []
                            for data in analyzed_data:
                                text = data['text']
                                predictions = data['predictions']
                                bg_color = emotion_colors.get(predictions[0]['label'], '#ccc')

                                tooltip_table = '<table style="font-size: 16px">'
                                tooltip_table += ('<p style="text-align: center; '
                                                  'font-weight: bold">Most likely emotions<p>')
                                for p in predictions:
                                    score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                    tooltip_table += (
                                        f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{p["label"]}</td>'
                                        f'<td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{score_to_display}</td></tr>'
                                    )
                                tooltip_table += '</table>'

                                span_html = f'''
                                <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
                                    {text}
                                    <span class="tooltiptext">{tooltip_table}</span>
                                </span>
                                '''
                                if last_paragraph_id != data['paragraphIndex']:
                                    span_html = '<br>' + span_html
                                    last_paragraph_id = data['paragraphIndex']
                                parts.append(span_html)

                            ui.add_head_html('''
                            <style>
                            .tooltip {
                                position: relative;
                                display: inline;
                                cursor: pointer;
                                white-space: normal;
                            }
                            .tooltip .tooltiptext {
                                visibility: hidden;
                                background-color: #f9f9f9;
                                color: #000;
                                text-align: left;
                                border-radius: 6px;
                                border: 1px solid #ccc;
                                padding: 6px;
                                position: absolute;
                                z-index: 9999;
                                top: 1.5em;
                                left: 0;
                                opacity: 0;
                                transition: opacity 0.2s;
                                white-space: nowrap;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                            }
                            .tooltip:hover .tooltiptext {
                                visibility: visible;
                                opacity: 1;
                            }
                            </style>
                            ''')

                            joined_html = ' '.join(parts)
                            ui.html(f'<div style="font-size: 18px; line-height: 1.6; '
                                    f'text-align: justify;">{joined_html}</div>')
                            ui.button('Clear', color='#808080', on_click=lambda: card_container.clear()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')
            with ui.column().classes('items-center gap-0 self-end'):
                top_n = ui.number(value=1).classes('self-center w-[180px]')
                top_n.min = 1
                top_n.max = len(emotion_colors)
                top_n.label = '# of emotions'
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.column().classes('mt-[20px] w-[1000px]')
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
                analyzed_data = create_request(description.value, top_n_propaganda.value, top_n_emotions.value)
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.card():
                            last_paragraph_id = 0
                            parts = []
                            for idx, data in enumerate(analyzed_data['propaganda_analyzed']):
                                text = data['text']
                                predictions = data['predictions']
                                bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                tooltip_table = '<table style="font-size: 16px">'
                                tooltip_table += ('<p style="text-align: center; '
                                                  'font-weight: bold">Most likely propaganda techniques<p>')
                                for p in predictions:
                                    score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                    tooltip_table += (
                                        f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{p["label"]}</td>'
                                        f'<td style="padding: 2px 8px; white-space: nowrap; '
                                        f'border: 1px solid black;">{score_to_display}</td></tr>'
                                    )
                                tooltip_table += '</table>'
                                span_html = f'''
                                <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
                                    {text}
                                    <span class="tooltiptext">{tooltip_table}</span>
                                </span>
                                '''
                                paragraph_tooltip = '''
                                <span class="paragraph-tooltiptext"><table style="font-size: 16px">
                                    <p style="text-align: center; font-weight: bold">
                                    Most likely paragraph's emotions</p>'''
                                for emotions_data in analyzed_data['emotions_analyzed']:
                                    if data['paragraphIndex'] == emotions_data['paragraphIndex']:
                                        for p in emotions_data['predictions']:
                                            score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                            paragraph_tooltip += (
                                                f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                                f'border: 1px solid black;">{p["label"]}</td>'
                                                f'<td style="padding: 2px 8px; white-space: nowrap; '
                                                f'border: 1px solid black;">{score_to_display}</td></tr>'
                                            )
                                paragraph_tooltip += '</table></span>'
                                if not idx:
                                    paragraph_id = data['paragraphIndex']
                                    span_html = (f'<div class="paragraph-tooltip paragraph_{paragraph_id}" '
                                                 f'style="margin_bottom: -20px">{paragraph_tooltip}') + span_html
                                if last_paragraph_id != data['paragraphIndex']:
                                    paragraph_id = data['paragraphIndex']
                                    span_html = (f'</div><div class="paragraph-tooltip paragraph_{paragraph_id}">'
                                                 f'{paragraph_tooltip}') + span_html
                                    last_paragraph_id = data['paragraphIndex']
                                parts.append(span_html)

                            ui.add_head_html('''
                            <style>
                            .tooltip {
                                position: relative;
                                display: inline;
                                cursor: pointer;
                                white-space: normal;
                            }
                            .tooltip .tooltiptext {
                                visibility: hidden;
                                background-color: #f9f9f9;
                                color: #000;
                                text-align: left;
                                border-radius: 6px;
                                border: 1px solid #ccc;
                                padding: 6px;
                                position: absolute;
                                z-index: 9999;
                                top: 1.5em;
                                left: 0;
                                opacity: 0;
                                transition: opacity 0.2s;
                                white-space: nowrap;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                            }
                            .tooltip:hover .tooltiptext {
                                visibility: visible;
                                opacity: 1;
                            }
                            .paragraph-tooltiptext {
                                visibility: hidden;
                                background-color: #f9f9f9;
                                color: #000;
                                border-radius: 6px;
                                border: 1px solid #ccc;
                                padding: 6px;
                                position: absolute;
                                z-index: 9999;
                                top: 0px;
                                width: 290px;
                                left: -300px;
                                opacity: 0;
                                transition: opacity 0.2s;
                                white-space: nowrap;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                            }
                            .paragraph-tooltip:hover .paragraph-tooltiptext {
                                visibility: visible;
                                opacity: 1;
                            }
                            .tooltip:hover ~ .paragraph-tooltiptext,
                            .tooltip:hover + .paragraph-tooltiptext,
                            .tooltip:hover .paragraph-tooltiptext {
                                visibility: hidden !important;
                                opacity: 0 !important;
                            }
                            </style>
                            ''')
                            parts[-1] += '</div>'
                            joined_html = ' '.join(parts)
                            ui.html(f'<div style="font-size: 18px; line-height: 1.6; '
                                    f'text-align: justify;">{joined_html}</div>')
                            ui.button('Clear', color='#808080', on_click=lambda: card_container.clear()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')
            with ui.column().classes('items-center gap-0 self-end'):
                top_n_propaganda = ui.number(value=1).classes('self-center w-[180px]')
                top_n_propaganda.min = 1
                top_n_propaganda.max = len(propaganda_colors)
                top_n_propaganda.label = '# of propaganda techniques'
                top_n_emotions = ui.number(value=1).classes('self-center w-[180px]')
                top_n_emotions.min = 1
                top_n_emotions.max = len(emotion_colors)
                top_n_emotions.label = '# of emotions'
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_response(analyze_result):
    render_header()
    ui.label(analyze_result).classes('text-[32px] text-black text-bold')
    render_footer()


def render_error():
    render_header()
    ui.label('An error occurred').classes('text-[32px] text-black text-bold')
    render_footer()
