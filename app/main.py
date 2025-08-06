from fastapi import FastAPI

from app.request.router import router as request_router
from app.tools import emotions_model_download, manipulations_model_download, propaganda_model_download

propaganda_model_download.ensure_model()
manipulations_model_download.ensure_model()
emotions_model_download.ensure_model()

app = FastAPI()

app.include_router(request_router)


@app.get('/')
async def health_check():
    return {'status': 'ok'}
