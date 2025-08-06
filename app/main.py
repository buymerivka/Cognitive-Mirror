from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.request.router import router as request_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(request_router)


@app.get('/')
async def health_check():
    return {'status': 'ok'}
