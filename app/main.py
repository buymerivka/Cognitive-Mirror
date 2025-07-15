from fastapi import FastAPI

from app.request.router import router as request_router

app = FastAPI()

app.include_router(request_router)


@app.get('/')
async def health_check():
    return {'status': 'ok'}
