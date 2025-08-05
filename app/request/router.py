import io
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.request.schemas import RequestSchema, ResponseSchema, TotalResponseSchema
from app.tools import bias_classifier
from app.tools.emotion_classifier import text_classify_by_paragraph, text_classify_by_sentence
from app.tools.preprocessor import preprocessing

router = APIRouter(tags=['analyser'])


@router.post('/analyze_propaganda', response_model=ResponseSchema)
async def analyze_propaganda(request_data: RequestSchema, top_n: int = 1):
    clf = bias_classifier.BiasClassifier()
    clf.load()
    initial_data = preprocessing(request_data.input_data)
    analyzed_text = clf.predict([data.text for data in initial_data], top_n=top_n)

    for idx, data in enumerate(analyzed_text):
        data['paragraphIndex'] = initial_data[idx].paragraphIndex
        data['sentenceIndex'] = initial_data[idx].sentenceIndex
        data['charStart'] = initial_data[idx].charStart
        data['charEnd'] = initial_data[idx].charEnd

    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze_emotions', response_model=ResponseSchema)
async def analyze_emotions(request_data: RequestSchema, top_n: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data, top_n)
    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze', response_model=TotalResponseSchema)
async def analyze(request_data: RequestSchema, top_n_propaganda: int = 1, top_n_emotions: int = 1):
    clf = bias_classifier.BiasClassifier()
    clf.load()
    initial_data = preprocessing(request_data.input_data)
    analyzed_propaganda = clf.predict([data.text for data in initial_data], top_n=top_n_propaganda)

    for idx, data in enumerate(analyzed_propaganda):
        data['paragraphIndex'] = initial_data[idx].paragraphIndex
        data['sentenceIndex'] = initial_data[idx].sentenceIndex
        data['charStart'] = initial_data[idx].charStart
        data['charEnd'] = initial_data[idx].charEnd

    analyzed_emotion = text_classify_by_paragraph(request_data.input_data, top_n_emotions)
    return TotalResponseSchema.model_validate({
        'propaganda_analyzed': analyzed_propaganda,
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
