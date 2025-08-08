import os

from dotenv import load_dotenv
from nicegui import ui

from colors_tool import emotion_colors, propaganda_colors
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
        result_container = ui.row().classes('mt-[20px] w-full')
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

            analyzed_data = None

            checkbox_states = {'none': True,
                               'false dilemma': True,
                               'slippery slope': True,
                               'appeal to nature': True,
                               'appeal to authority': True,
                               'appeal to majority': True,
                               'hasty generalization': True,
                               'appeal to worse problems': True,
                               'appeal to tradition': True
                               }
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
                    analyzed_data = create_request_propaganda(description.value, 9)
                if analyzed_data is None:
                    ui.notify('An error occurred', color='red')
                else:
                    result_container.clear()
                    with result_container:
                        with ui.column().classes(
                                'mt-[20px] w-full max-w-[300px] rounded-[12px] p-[20px] shadow-md') as filter_container:
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

                            ui.button('Apply filters', color='#808080', on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px]') as card_container:
                            with ui.card():
                                last_paragraph_id = 0
                                parts = []
                                selected_techniques = [tech for tech in checkbox_states.keys() if checkbox_states[tech]]
                                for data in analyzed_data:
                                    text = data['text']
                                    predictions = data['predictions']
                                    if predictions[0]['label'] not in selected_techniques and predictions[0][
                                        'label'] != 'none':
                                        bg_color = propaganda_colors.get('none', '#ccc')
                                    else:
                                        bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += ('<p style="text-align: center; '
                                                      'font-weight: bold">Most likely propaganda techniques<p>')
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
                                            <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
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
                                ui.button('Clear', color='#808080', on_click=lambda: (result_container.clear(),
                                                                                      clear_action())).classes(
                                    'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                # top_n = ui.number(value=1).classes('self-center w-[180px]')
                # top_n.min = 1
                # top_n.max = len(propaganda_colors)
                # top_n.label = '# of propaganda techniques'
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_emotions_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        result_container = ui.row().classes('mt-[20px] w-full')
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

            analyzed_data = None

            checkbox_states = {'admiration': True,
                               'amusement': True,
                               'anger': True,
                               'annoyance': True,
                               'approval': True,
                               'caring': True,
                               'confusion': True,
                               'curiosity': True,
                               'desire': True,
                               'disappointment': True,
                               'disapproval': True,
                               'disgust': True,
                               'embarrassment': True,
                               'excitement': True,
                               'fear': True,
                               'gratitude': True,
                               'grief': True,
                               'joy': True,
                               'love': True,
                               'nervousness': True,
                               'optimism': True,
                               'pride': True,
                               'realization': True,
                               'relief': True,
                               'remorse': True,
                               'sadness': True,
                               'surprise': True,
                               'neutral': True
                               }
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
                    analyzed_data = create_request_emotions(description.value, 28)
                if analyzed_data is None:
                    ui.notify('An error occurred', color='red')
                else:
                    result_container.clear()
                    with result_container:
                        with ui.column().classes(
                                'mt-[20px] w-full max-w-[300px] rounded-[12px] p-[20px] shadow-md') as filter_container:
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

                            ui.button('Apply filters', color='#808080', on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px]') as card_container:
                            with ui.card():
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

                                    for p in filtered_predictions[:min(9, amount)]:
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
                                            <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
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
                                ui.button('Clear', color='#808080', on_click=lambda: (result_container.clear(),
                                                                                      clear_action())).classes(
                                    'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                # top_n = ui.number(value=1).classes('self-center w-[180px]')
                # top_n.min = 1
                # top_n.max = len(emotion_colors)
                # top_n.label = '# of emotions'
                ui.button('Send a request', color='#2c2c2c', on_click=create_on_click).classes(
                    'w-[270px] h-[40px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] ml-[20px] mt-[10px] mt-[46px] '
                    'self-end')

    render_footer()


def render_analyze_request():
    render_header()
    with ui.column().classes('w-full justify-center items-center'):
        ui.label('Create a request').classes('text-[17px] mb-[10px] text-[24px] font-bold justify-center')
        result_container = ui.row().classes('mt-[20px] w-full')
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

            analyzed_data = None

            checkbox_propaganda = {'none': True,
                                   'false dilemma': True,
                                   'slippery slope': True,
                                   'appeal to nature': True,
                                   'appeal to authority': True,
                                   'appeal to majority': True,
                                   'hasty generalization': True,
                                   'appeal to worse problems': True,
                                   'appeal to tradition': True
                                   }
            checkbox_propaganda_elements = {}

            checkbox_emotions = {'admiration': True,
                                 'amusement': True,
                                 'anger': True,
                                 'annoyance': True,
                                 'approval': True,
                                 'caring': True,
                                 'confusion': True,
                                 'curiosity': True,
                                 'desire': True,
                                 'disappointment': True,
                                 'disapproval': True,
                                 'disgust': True,
                                 'embarrassment': True,
                                 'excitement': True,
                                 'fear': True,
                                 'gratitude': True,
                                 'grief': True,
                                 'joy': True,
                                 'love': True,
                                 'nervousness': True,
                                 'optimism': True,
                                 'pride': True,
                                 'realization': True,
                                 'relief': True,
                                 'remorse': True,
                                 'sadness': True,
                                 'surprise': True,
                                 'neutral': True
                                 }
            checkbox_emotions_elements = {}
            first_run = True

            def clear_action():
                nonlocal first_run, analyzed_data, checkbox_emotions, checkbox_propaganda
                for technique in checkbox_emotions:
                    checkbox_emotions[technique] = True
                for technique in checkbox_propaganda:
                    checkbox_propaganda[technique] = True
                analyzed_data = None
                first_run = True

            def create_on_click():
                nonlocal first_run, analyzed_data, checkbox_emotions, checkbox_propaganda, checkbox_emotions_elements, checkbox_propaganda_elements
                if not description.value:
                    ui.notify('Text is required', color='red')
                    return
                if first_run:
                    analyzed_data = create_request(description.value, 9, 28)
                if not analyzed_data:
                    ui.notify('An error occurred', color='red')
                else:
                    result_container.clear()
                    with result_container:
                        with ui.column().classes(
                                'mt-[20px] w-full max-w-[300px] rounded-[12px] p-[20px] shadow-md') as filter_container:
                            ui.label('Filters:').classes('text-xl font-bold mb-4')

                            ui.label('Show manipulation techniques:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_propaganda.keys():
                                    if technique != 'none':
                                        checkbox_propaganda_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_propaganda[technique],
                                            on_change=lambda e, t=technique: checkbox_propaganda.__setitem__(t, e.value)
                                        )

                            ui.label('Show emotions:').classes('text-[16px] mt-[10px] mb-[5px]')

                            with ui.column().classes(
                                    'max-h-[300px] w-[200px] overflow-y-auto rounded-[12px] p-[20px] shadow-md'):
                                for technique in checkbox_emotions.keys():
                                    if technique != 'neutral':
                                        checkbox_emotions_elements[technique] = ui.checkbox(
                                            technique,
                                            value=checkbox_emotions[technique],
                                            on_change=lambda e, t=technique: checkbox_emotions.__setitem__(t, e.value)
                                        )

                            ui.button('Apply filters', color='#808080', on_click=lambda: create_on_click()).classes(
                                'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

                        with ui.column().classes('mt-[20px] w-[1000px]') as card_container:
                            with ui.card():
                                last_paragraph_id = 0
                                parts = []
                                selected_propaganda_techniques = [tech for tech in checkbox_propaganda.keys() if
                                                                  checkbox_propaganda[tech]]
                                for data in analyzed_data['propaganda_analyzed']:
                                    text = data['text']
                                    predictions = data['predictions']
                                    if predictions[0]['label'] not in selected_propaganda_techniques and predictions[0][
                                        'label'] != 'none':
                                        bg_color = propaganda_colors.get('none', '#ccc')
                                    else:
                                        bg_color = propaganda_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += ('<p style="text-align: center; '
                                                      'font-weight: bold">Most likely propaganda techniques<p>')
                                    for p in predictions:
                                        if p['label'] in selected_propaganda_techniques:
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
                                            <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
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
                                paragraph_tooltip = '''
                                <span class="paragraph-tooltiptext"><table style="font-size: 16px">
                                    <p style="text-align: center; font-weight: bold">
                                    Most likely paragraph's emotions</p>'''

                                selected_emotions_techniques = [tech for tech in checkbox_emotions.keys() if
                                                                checkbox_emotions[tech]]
                                for data in analyzed_data['emotions_analyzed']:
                                    text = data['text']
                                    predictions = data['predictions']
                                    if predictions[0]['label'] not in selected_emotions_techniques and predictions[0][
                                        'label'] != 'neutral':
                                        bg_color = emotion_colors.get('neutral', '#ccc')
                                    else:
                                        bg_color = emotion_colors.get(predictions[0]['label'], '#ccc')

                                    tooltip_table = '<table style="font-size: 16px">'
                                    tooltip_table += ('<p style="text-align: center; '
                                                      'font-weight: bold">Most likely emotions<p>')

                                    amount = len(selected_emotions_techniques)

                                    filtered_predictions = [p for p in predictions if
                                                            p['label'] in selected_emotions_techniques]

                                    for p in filtered_predictions[:min(9, amount)]:
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
                                            <span class="tooltip" style="background-color: {bg_color}; padding: 2px 4px">
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
                                ui.button('Clear', color='#808080',
                                          on_click=lambda: (result_container.clear(), clear_action())).classes(
                                    'w-[270px] h-[30px] rounded-[8px] text-white bg-[rgb(44, 44, 44)] self-end')

            with ui.column().classes('items-center gap-0 self-end'):
                # top_n_propaganda = ui.number(value=1).classes('self-center w-[180px]')
                # top_n_propaganda.min = 1
                # top_n_propaganda.max = len(propaganda_colors)
                # top_n_propaganda.label = '# of propaganda techniques'
                # top_n_emotions = ui.number(value=1).classes('self-center w-[180px]')
                # top_n_emotions.min = 1
                # top_n_emotions.max = len(emotion_colors)
                # top_n_emotions.label = '# of emotions'
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
