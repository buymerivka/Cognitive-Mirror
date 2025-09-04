import io
import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.request.schemas import FullResponseSchema, RequestSchema, ResponseSchema
from app.tools.classifier import text_classify_by_sentence, text_full_classify

router = APIRouter(tags=['analyser'])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROPAGANDA_MAX = 5
MANIPULATIONS_MAX = 9
EMOTIONS_MAX = 28


@router.post('/analyze_manipulations', response_model=ResponseSchema)
async def analyze_manipulations(request_data: RequestSchema, top_n_manipulations: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data,
                                              f'{BASE_DIR}/models/manipulations_bert_model',
                                              f'{BASE_DIR}/models/manipulations_bert_model/tokenizer',
                                              top_n_manipulations,
                                              MANIPULATIONS_MAX)

    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze_emotions', response_model=ResponseSchema)
async def analyze_emotions(request_data: RequestSchema, top_n_emotions: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data,
                                              f'{BASE_DIR}/models/bert-goemotions',
                                              f'{BASE_DIR}/models/bert-goemotions',
                                              top_n_emotions,
                                              EMOTIONS_MAX)
    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze', response_model=FullResponseSchema)
async def analyze(request_data: RequestSchema, top_n_propaganda: int = 1, top_n_manipulations: int = 1,
                  top_n_emotions: int = 1):
    full_analysis = text_full_classify(request_data.input_data,
                                       f'{BASE_DIR}/models/propaganda_bert_model',
                                       f'{BASE_DIR}/models/propaganda_bert_model/tokenizer',
                                       f'{BASE_DIR}/models/manipulations_bert_model',
                                       f'{BASE_DIR}/models/manipulations_bert_model/tokenizer',
                                       f'{BASE_DIR}/models/bert-goemotions',
                                       f'{BASE_DIR}/models/bert-goemotions',
                                       PROPAGANDA_MAX,
                                       MANIPULATIONS_MAX,
                                       EMOTIONS_MAX,
                                       top_n_propaganda,
                                       top_n_manipulations,
                                       top_n_emotions)

    return FullResponseSchema.model_validate(full_analysis)


@router.post('/analyze_propaganda', response_model=ResponseSchema)
async def analyze_propaganda(request_data: RequestSchema, top_n_propaganda: int = 1):
    analyzed_propaganda = text_classify_by_sentence(request_data.input_data,
                                                    f'{BASE_DIR}/models/propaganda_bert_model',
                                                    f'{BASE_DIR}/models/propaganda_bert_model/tokenizer',
                                                    top_n_propaganda,
                                                    PROPAGANDA_MAX)
    return ResponseSchema.model_validate({
        'analyzed_data': analyzed_propaganda
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
