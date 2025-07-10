from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.request.schemas import RequestSchema

router = APIRouter(prefix='/analyze', tags=['analyser'])

@router.post('/analyze', response_model=[])
def analyze(request_data: RequestSchema):
    return JSONResponse(status_code=200, content={'details':'Data received successfully.'})
