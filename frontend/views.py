import os

from colors_tool import emotion_colors, manipulations_colors, propaganda_colors
from dotenv import load_dotenv
from nicegui import ui
from services import (
    create_request,
    create_request_emotions,
    create_request_manipulations,
    create_request_propaganda,
    download_json,
)

load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')
PROPAGANDA_MAX = 5
MANIPULATIONS_MAX = 9
EMOTIONS_MAX = 28


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


def render_analyze_manipulations_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.row().classes('card_container mt-[20px] w-full justify-center')
        with ui.row().classes('w-[1000px] max-w-[1000px] gap-0 justify-center self-center'):
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

            analyzed_data = None

            checkbox_states = {p: True for p in manipulations_colors.keys()}

            checkbox_elements = {}
            first_run = True

            def clear_action():
                nonlocal first_run, analyzed_data, checkbox_states
                for technique in checkbox_states:
                    checkbox_states[technique] = True
                analyzed_data = None
                first_run = True

            def create_on_click():
                nonlocal analyzed_data, checkbox_states, first_run, checkbox_elements
                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                if first_run:
                    analyzed_data = create_request_manipulations(description.value, len(manipulations_colors))
                if analyzed_data is None:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.column().classes(
                                'mt-[20px] max-w-[300px] rounded-[12px] p-[20px] shadow-md'):
                            ui.label('Filters:').classes('text-xl font-bold mb-4')
                            ui.label('Show manipulation techniques:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_states.keys():
                                    if technique != 'none':
                                        checkbox_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_states[technique],
                                            on_change=lambda e, t=technique: checkbox_states.__setitem__(t, e.value)
                                        )

                            ui.button('Apply filters', color='#808080',
                                      on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px] w-max-[1300px]'):
                            with ui.card().classes('w-full'):
                                last_paragraph_id = 0
                                parts = []
                                selected_techniques = [tech for tech in checkbox_states.keys() if checkbox_states[tech]]
                                for data in analyzed_data:
                                    text = data['text']
                                    predictions = data['predictions']
                                    if predictions[0]['label'] not in selected_techniques and predictions[0][
                                        'label'] != 'none':
                                        bg_color = manipulations_colors.get('none', '#ccc')
                                    else:
                                        bg_color = manipulations_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += ('<p style="text-align: center; '
                                                      'font-weight: bold">Most likely manipulations techniques<p>')
                                    for p in predictions:
                                        if p['label'] in selected_techniques:
                                            score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                            tooltip_table += (
                                                f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                                f'border: 1px solid black;">{p["label"]}</td>'
                                                f'<td style="padding: 2px 8px; white-space: nowrap; '
                                                f'border: 1px solid black;">{score_to_display}</td></tr>'
                                            )
                                    tooltip_table += '</table>'

                                    show_tooltip = (
                                            predictions and
                                            predictions[0].get('label') not in [None, 'none'] and
                                            bg_color.lower() != '#ffffff'
                                    )

                                    if show_tooltip:
                                        span_html = f'''
                                            <span class="tooltip" style="background-color: {bg_color};
                                            padding: 2px 4px">
                                                {text}
                                                <span class="tooltiptext">{tooltip_table}</span>
                                            </span>
                                        '''
                                    else:
                                        span_html = f'''
                                            <span style="background-color: {bg_color}; padding: 2px 4px">
                                                {text}
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

                                def call_download_json():
                                    print('Download initiated.')
                                    download_json(analyzed_data)
                                    print('Download finished.')
                                    return

                                with ui.row().classes('w-[430px] self-end gap-0'):
                                    ui.button('Download JSON', color='green', on_click=call_download_json).classes(
                                        'w-[210px] rounded-[8px] h-[30px] m-0 mr-[10px] self-end')
                                    ui.button('Clear', color='#808080', on_click=lambda: (card_container.clear(),
                                                                                          clear_action())).classes(
                                        'w-[210px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_emotions_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.row().classes('card_container mt-[20px] w-full justify-center')
        with ui.row().classes('w-[1000px] max-w-[1000px] gap-0 justify-center self-center'):
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

            analyzed_data = None

            checkbox_states = {p: True for p in emotion_colors.keys()}

            checkbox_elements = {}
            first_run = True

            def clear_action():
                nonlocal first_run, analyzed_data, checkbox_states
                for technique in checkbox_states:
                    checkbox_states[technique] = True
                analyzed_data = None
                first_run = True

            def create_on_click():
                nonlocal analyzed_data, checkbox_states, first_run, checkbox_elements
                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                if first_run:
                    analyzed_data = create_request_emotions(description.value, len(emotion_colors))
                if analyzed_data is None:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.column().classes(
                                'mt-[20px] max-w-[300px] rounded-[12px] p-[20px] shadow-md'):
                            ui.label('Filters:').classes('text-xl font-bold mb-4')
                            ui.label('Show emotions:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_states.keys():
                                    if technique != 'neutral':
                                        checkbox_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_states[technique],
                                            on_change=lambda e, t=technique: checkbox_states.__setitem__(t, e.value)
                                        )

                            ui.button('Apply filters', color='#808080',
                                      on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px] w-max-[1300px]'):
                            with ui.card().classes('w-full'):
                                last_paragraph_id = 0
                                parts = []
                                selected_techniques = [tech for tech in checkbox_states.keys() if checkbox_states[tech]]
                                for data in analyzed_data:
                                    text = data['text']
                                    predictions = data['predictions']
                                    if predictions[0]['label'] not in selected_techniques and predictions[0][
                                        'label'] != 'neutral':
                                        bg_color = emotion_colors.get('neutral', '#ccc')
                                    else:
                                        bg_color = emotion_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += ('<p style="text-align: center; '
                                                      'font-weight: bold">Most likely emotions<p>')

                                    amount = len(selected_techniques)

                                    filtered_predictions = [p for p in predictions if p['label'] in selected_techniques]

                                    for p in filtered_predictions[:min(len(manipulations_colors), amount)]:
                                        score_to_display = str(int(float(p['score']) * 10000) / 100) + '%'
                                        tooltip_table += (
                                            f'<tr><td style="padding: 2px 8px; white-space: nowrap; '
                                            f'border: 1px solid black;">{p["label"]}</td>'
                                            f'<td style="padding: 2px 8px; white-space: nowrap; '
                                            f'border: 1px solid black;">{score_to_display}</td></tr>'
                                        )
                                    tooltip_table += '</table>'

                                    show_tooltip = (
                                            predictions and
                                            predictions[0].get('label') not in [None, 'neutral'] and
                                            bg_color.lower() != '#ffffff'
                                    )

                                    if show_tooltip:
                                        span_html = f'''
                                            <span class="tooltip" style="background-color: {bg_color};
                                            padding: 2px 4px">
                                                {text}
                                                <span class="tooltiptext">{tooltip_table}</span>
                                            </span>
                                        '''
                                    else:
                                        span_html = f'''
                                            <span style="background-color: {bg_color}; padding: 2px 4px">
                                                {text}
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

                                def call_download_json():
                                    print('Download initiated.')
                                    download_json(analyzed_data)
                                    print('Download finished.')
                                    return

                                with ui.row().classes('w-[430px] self-end gap-0'):
                                    ui.button('Download JSON', color='green', on_click=call_download_json).classes(
                                        'w-[210px] rounded-[8px] h-[30px] m-0 mr-[10px] self-end')
                                    ui.button('Clear', color='#808080', on_click=lambda: (card_container.clear(),
                                                                                          clear_action())).classes(
                                        'w-[210px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_request():
    render_header()
    with (((ui.column().classes('w-full justify-center items-center')))):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.row().classes('card_container mt-[20px] w-full justify-center')
        with ui.row().classes('w-[1000px] max-w-[1000px] gap-0 justify-center self-center'):
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

            analyzed_data = None
            checkbox_propaganda = {p: True for p in propaganda_colors.keys()}
            checkbox_propaganda_elements = {}
            checkbox_manipulations = {m: True for m in manipulations_colors.keys()}
            checkbox_manipulations_elements = {}
            checkbox_emotions = {e: True for e in emotion_colors.keys()}
            checkbox_emotions_elements = {}

            first_run = True

            def clear_action():
                nonlocal first_run, analyzed_data, checkbox_propaganda
                for technique in checkbox_propaganda:
                    checkbox_propaganda[technique] = True
                analyzed_data = None
                first_run = True

            def create_on_click():
                nonlocal first_run, analyzed_data, checkbox_propaganda, checkbox_propaganda_elements, \
                    checkbox_manipulations, checkbox_manipulations_elements, \
                    checkbox_emotions, checkbox_emotions_elements

                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                if first_run:
                    analyzed_data = create_request(description.value, len(propaganda_colors), len(manipulations_colors),
                                                   len(emotion_colors))
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.column().classes(
                                'mt-[20px] max-w-[300px] rounded-[12px] p-[20px] shadow-md'):
                            ui.label('Filters:').classes('text-xl font-bold mb-4')

                            ui.label('Show propaganda strategies:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for strategy in checkbox_propaganda.keys():
                                    if strategy != 'none':
                                        checkbox_propaganda_elements[strategy] = ui.checkbox(
                                            strategy,
                                            value=checkbox_propaganda[strategy],
                                            on_change=lambda e,
                                                             t=strategy: checkbox_propaganda.__setitem__(t, e.value)
                                        )

                            ui.label('Show manipulations tehniques:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_manipulations.keys():
                                    if technique != 'none':
                                        checkbox_manipulations_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_manipulations[technique],
                                            on_change=lambda e,
                                                             t=technique: checkbox_manipulations.__setitem__(t, e.value)
                                        )

                            ui.label('Show emotions:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for emotion in checkbox_emotions.keys():
                                    if technique != 'none':
                                        checkbox_emotions_elements[emotion] = ui.checkbox(
                                            emotion,
                                            value=checkbox_emotions[emotion],
                                            on_change=lambda e,
                                                             t=emotion: checkbox_emotions.__setitem__(t, e.value)
                                        )

                            ui.button('Apply filters', color='#808080',
                                      on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px] w-max-[1300px]'):
                            with ui.card().classes('w-full'):
                                selected_propaganda_strategies = [strategy for strategy in checkbox_propaganda.keys() if
                                                                  checkbox_propaganda[strategy]]

                                selected_manipulations_techniques = [tech for tech in checkbox_manipulations.keys() if
                                                                     checkbox_manipulations[tech]]

                                selected_emotions = [emotion for emotion in checkbox_emotions.keys() if
                                                     checkbox_emotions[emotion]]

                                paragraphs = {}

                                last_paragraph_id = 0
                                parts = []

                                for data in analyzed_data['propaganda_analyzed']:
                                    text = data['text']
                                    predictions = data['predictions']

                                    if (predictions[0]['label'] not in selected_propaganda_strategies and
                                            predictions[0]['label'] != 'general discourse'):
                                        bg_color = propaganda_colors.get('general discourse', '#ccc')
                                    else:
                                        bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += (
                                        '<p style="text-align: left; '
                                        'font-weight: bold">Most likely propaganda strategy: <p>')

                                    if predictions[0]['label'] in selected_propaganda_strategies:
                                        score_to_display = f"{int(float(predictions[0]['score']) * 10000) / 100}%"
                                        tooltip_table += (
                                            f'<tr><td style="padding: 2px 8px; white-space: nowrap; border: '
                                            f'1px solid black;">{predictions[0]["label"]}</td>'
                                            f'<td style="padding: 2px 8px; white-space: nowrap; '
                                            f'border: 1px solid black;">{score_to_display}</td></tr>'
                                        )

                                    tooltip_table += '</table>'

                                    for manipulations_data in analyzed_data['manipulations_analyzed']:
                                        if manipulations_data['text'] == text:
                                            i = 0
                                            while manipulations_data['predictions'][i][
                                                'label'] not in selected_manipulations_techniques:
                                                i += 1
                                            if i < MANIPULATIONS_MAX:
                                                tooltip_table += '<table style="font-size: 16px">'
                                                tooltip_table += (
                                                    '<p style="text-align: left; '
                                                    'font-weight: bold">Most likely manipulations techniques: <p>')
                                                score_to_display = f"{int(float(
                                                    manipulations_data['predictions'][i]['score']) * 10000) / 100}%"
                                                tooltip_table += (
                                                    f'<tr><td style="padding: 2px 8px; white-space: nowrap; border: '
                                                    f'1px solid black;">{manipulations_data['predictions'][i]["label"]}'
                                                    f'</td>'
                                                    f'<td style="padding: 2px 8px; white-space: nowrap; '
                                                    f'border: 1px solid black;">{score_to_display}</td></tr>'
                                                )
                                                tooltip_table += '</table>'
                                    for emotions_data in analyzed_data['emotions_analyzed']:
                                        if emotions_data['text'] == text:
                                            i = 0
                                            while emotions_data['predictions'][i]['label'] not in selected_emotions:
                                                i += 1
                                            if i < EMOTIONS_MAX:
                                                tooltip_table += '<table style="font-size: 16px">'
                                                tooltip_table += (
                                                    '<p style="text-align: left; '
                                                    'font-weight: bold">Most likely emotions: <p>')
                                                score_to_display = f"{int(float(
                                                    emotions_data['predictions'][i]['score']) * 10000) / 100}%"
                                                tooltip_table += (
                                                    f'<tr><td style="padding: 2px 8px; white-space: nowrap; border: '
                                                    f'1px solid black;">{emotions_data['predictions'][i]["label"]}</td>'
                                                    f'<td style="padding: 2px 8px; white-space: nowrap; '
                                                    f'border: 1px solid black;">{score_to_display}</td></tr>'
                                                )
                                                tooltip_table += '</table>'

                                    show_tooltip = (
                                            predictions and
                                            predictions[0].get('label') not in [None, 'general discourse'] and
                                            bg_color.lower() != '#ffffff'
                                    )

                                    if show_tooltip:
                                        span_html = f'''
                                            <span class="tooltip" style="background-color: {bg_color};
                                            padding: 2px 4px; cursor: pointer;">
                                                {text}
                                                <span class="tooltiptext">{tooltip_table}</span>
                                            </span>
                                        '''
                                    else:
                                        span_html = f'''
                                            <span style="background-color: {bg_color}; padding: 2px 4px">
                                                {text}
                                            </span>
                                        '''

                                    if last_paragraph_id != data['paragraphIndex']:
                                        span_html = '<br>' + span_html
                                        last_paragraph_id = data['paragraphIndex']
                                    parts.append(span_html)

                                    paragraph_index = data['paragraphIndex']
                                    paragraphs.setdefault(paragraph_index, []).append(span_html)

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

                                def call_download_json():
                                    print('Download initiated.')
                                    download_json(analyzed_data)
                                    print('Download finished.')
                                    return

                                with ui.row().classes('w-[430px] self-end gap-0'):
                                    ui.button('Download JSON', color='green', on_click=call_download_json).classes(
                                        'w-[210px] rounded-[8px] h-[30px] m-0 mr-[10px] self-end')
                                    ui.button('Clear', color='#808080', on_click=lambda: (card_container.clear(),
                                                                                          clear_action())).classes(
                                        'w-[210px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_propaganda_request():
    render_header()
    with (((ui.column().classes('w-full justify-center items-center')))):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        card_container = ui.row().classes('card_container mt-[20px] w-full justify-center')
        with ui.row().classes('w-[1000px] max-w-[1000px] gap-0 justify-center self-center'):
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

            analyzed_data = None

            checkbox_propaganda = {p: True for p in propaganda_colors.keys()}

            checkbox_propaganda_elements = {}

            first_run = True

            def clear_action():
                nonlocal first_run, analyzed_data, checkbox_propaganda
                for technique in checkbox_propaganda:
                    checkbox_propaganda[technique] = True
                analyzed_data = None
                first_run = True

            def create_on_click():
                nonlocal first_run, analyzed_data, checkbox_propaganda, \
                    checkbox_propaganda_elements
                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                if first_run:
                    analyzed_data = create_request_propaganda(description.value, len(propaganda_colors))
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    card_container.clear()
                    with card_container:
                        with ui.column().classes(
                                'mt-[20px] max-w-[300px] rounded-[12px] p-[20px] shadow-md'):
                            ui.label('Filters:').classes('text-xl font-bold mb-4')

                            ui.label('Show propaganda strategies:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_propaganda.keys():
                                    if technique != 'none':
                                        checkbox_propaganda_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_propaganda[technique],
                                            on_change=lambda e,
                                                             t=technique: checkbox_propaganda.__setitem__(t, e.value)
                                        )

                            ui.button('Apply filters', color='#808080',
                                      on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px] w-max-[1300px]'):
                            with ui.card().classes('w-full'):
                                selected_propaganda_techniques = [tech for tech in checkbox_propaganda.keys() if
                                                                  checkbox_propaganda[tech]]

                                paragraphs = {}

                                last_paragraph_id = 0
                                parts = []

                                for data in analyzed_data['analyzed_data']:
                                    text = data['text']
                                    predictions = data['predictions']

                                    if (predictions[0]['label'] not in selected_propaganda_techniques and
                                            predictions[0]['label'] != 'general discourse'):
                                        bg_color = propaganda_colors.get('general discourse', '#ccc')
                                    else:
                                        bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += (
                                        '<p style="text-align: center; '
                                        'font-weight: bold">Most likely propaganda strategy: <p>')

                                    if predictions[0]['label'] in selected_propaganda_techniques:
                                        score_to_display = f"{int(float(predictions[0]['score']) * 10000) / 100}%"
                                        tooltip_table += (
                                            f'<tr><td style="padding: 2px 8px; white-space: nowrap; border: '
                                            f'1px solid black;">{predictions[0]["label"]}</td>'
                                            f'<td style="padding: 2px 8px; white-space: nowrap; '
                                            f'border: 1px solid black;">{score_to_display}</td></tr>'
                                        )

                                    tooltip_table += '</table>'

                                    show_tooltip = (
                                            predictions and
                                            predictions[0].get('label') not in [None, 'general discourse'] and
                                            bg_color.lower() != '#ffffff'
                                    )

                                    if show_tooltip:
                                        span_html = f'''
                                            <span class="tooltip" style="background-color: {bg_color};
                                            padding: 2px 4px; cursor: pointer;">
                                                {text}
                                                <span class="tooltiptext">{tooltip_table}</span>
                                            </span>
                                        '''
                                    else:
                                        span_html = f'''
                                            <span style="background-color: {bg_color}; padding: 2px 4px">
                                                {text}
                                            </span>
                                        '''

                                    if last_paragraph_id != data['paragraphIndex']:
                                        span_html = '<br>' + span_html
                                        last_paragraph_id = data['paragraphIndex']
                                    parts.append(span_html)

                                    paragraph_index = data['paragraphIndex']
                                    paragraphs.setdefault(paragraph_index, []).append(span_html)

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

                                def call_download_json():
                                    print('Download initiated.')
                                    download_json(analyzed_data)
                                    print('Download finished.')
                                    return

                                with ui.row().classes('w-[430px] self-end gap-0'):
                                    ui.button('Download JSON', color='green', on_click=call_download_json).classes(
                                        'w-[210px] rounded-[8px] h-[30px] m-0 mr-[10px] self-end')
                                    ui.button('Clear', color='#808080', on_click=lambda: (card_container.clear(),
                                                                                          clear_action())).classes(
                                        'w-[210px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
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
