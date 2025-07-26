from fastapi import APIRouter

from app.request.schemas import RequestSchema, ResponseSchema, TotalResponseSchema
from app.tools import bias_classifier
from app.tools.emotion_classifier import text_classify_by_paragraph, text_classify_by_sentence
from app.tools.preprocessor import preprocessing

router = APIRouter(tags=['analyser'])


@router.post('/analyze_propaganda', response_model=ResponseSchema)
async def analyze_propaganda(request_data: RequestSchema, top_n: int = 1):
    clf = bias_classifier.BiasClassifier()
    clf.load()
    analyzed_text = clf.predict([data.text for data in preprocessing(request_data.input_data)], top_n=top_n)

    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze_emotions', response_model=ResponseSchema)
async def analyze_emotions(request_data: RequestSchema, top_n: int = 1):
    analyzed_text = text_classify_by_sentence(request_data.input_data, top_n)
    return ResponseSchema.model_validate({'analyzed_data': analyzed_text})


@router.post('/analyze', response_model=TotalResponseSchema)
async def analyze(request_data: RequestSchema, top_n: int = 1):
    clf = bias_classifier.BiasClassifier()
    clf.load()
    analyzed_propaganda = clf.predict([data.text for data in preprocessing(request_data.input_data)], top_n=top_n)
    analyzed_emotion = text_classify_by_paragraph(request_data.input_data, top_n)

    return TotalResponseSchema.model_validate({
        'propaganda_analyzed': analyzed_propaganda,
        'emotions_analyzed': analyzed_emotion,
    })
