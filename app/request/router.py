import io
import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.request.schemas import RequestSchema, ResponseSchema, TotalResponseSchema, FullResponseSchema
from app.tools.classifier import text_classify_by_paragraph, text_classify_by_sentence

router = APIRouter(tags=['analyser'])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@router.post('/analyze_manipulations', response_model=ResponseSchema)
async def analyze_manipulations(request_data: RequestSchema, top_n: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data,
                                              f'{BASE_DIR}/models/manipulations_bert_model/checkpoint-504',
                                              f'{BASE_DIR}/models/manipulations_bert_model/tokenizer', top_n, 9)

    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze_emotions', response_model=ResponseSchema)
async def analyze_emotions(request_data: RequestSchema, top_n: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data, f'{BASE_DIR}/models/bert-goemotions',
                                              f'{BASE_DIR}/models/bert-goemotions', top_n, 28)
    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze', response_model=TotalResponseSchema)
async def analyze(request_data: RequestSchema, top_n_manipulations: int = 1, top_n_emotions: int = 1):
    analyzed_manipulations = text_classify_by_sentence(request_data.input_data,
                                                       f'{BASE_DIR}/models/manipulations_bert_model/checkpoint-504',
                                                       f'{BASE_DIR}/models/manipulations_bert_model/tokenizer',
                                                       top_n_manipulations, 9)

    analyzed_emotion = text_classify_by_paragraph(request_data.input_data, f'{BASE_DIR}/models/bert-goemotions',
                                                  f'{BASE_DIR}/models/bert-goemotions', top_n_emotions, 28)
    return TotalResponseSchema.model_validate({
        'manipulations_analyzed': analyzed_manipulations,
        'emotions_analyzed': analyzed_emotion,
    })


@router.post('/analyze_propaganda', response_model=FullResponseSchema)
async def analyze(request_data: RequestSchema, top_n_manipulations: int = 1, top_n_emotions: int = 1,
                  top_n_propaganda: int = 1):
    analyzed_propaganda = text_classify_by_sentence(request_data.input_data,
                                                    f'{BASE_DIR}/models/propaganda_bert_model/checkpoint-2220',
                                                    f'{BASE_DIR}/models/propaganda_bert_model/tokenizer',
                                                    top_n_propaganda, 5)

    analyzed_manipulations = text_classify_by_sentence(request_data.input_data,
                                                       f'{BASE_DIR}/models/manipulations_bert_model/checkpoint-504',
                                                       f'{BASE_DIR}/models/manipulations_bert_model/tokenizer',
                                                       top_n_manipulations, 9)

    analyzed_emotion = text_classify_by_paragraph(request_data.input_data, f'{BASE_DIR}/models/bert-goemotions',
                                                  f'{BASE_DIR}/models/bert-goemotions', top_n_emotions, 28)
    return FullResponseSchema.model_validate({
        'propaganda_analyzed': analyzed_propaganda,
        'manipulations_analyzed': analyzed_manipulations,
        'emotions_analyzed': analyzed_emotion,
    })


@router.post('/download-json')
async def download_json(request: Request):
    data = await request.json()

    json_bytes = json.dumps(data, indent=4).encode('utf-8')
    file_like = io.BytesIO(json_bytes)

    return StreamingResponse(
        file_like,
        media_type='application/json',
        headers={'Content-Disposition': 'attachment; filename=data.json'}
    )
