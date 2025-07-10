from fastapi import APIRouter

from app.request.schemas import RequestSchema, ResponseSchema
from app.tools.preprocessor import preprocessing

router = APIRouter(prefix='/analyze', tags=['analyser'])


@router.post('/', response_model=ResponseSchema)
async def analyze(request_data: RequestSchema):
    parsed_text = preprocessing(request_data.input_data)
    result: list[dict] = []
    for sentence_info in parsed_text:
        result.append({
            'paragraphIndex': sentence_info.paragraphIndex,
            'sentenceIndex': sentence_info.sentenceIndex,
            'text': sentence_info.text,
            'charStart': sentence_info.charStart,
            'charEnd': sentence_info.charEnd
        })
    return ResponseSchema.parse_obj({'parsed_data': result})
