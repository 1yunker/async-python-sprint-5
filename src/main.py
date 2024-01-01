import aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.v1 import base
from core import logger
from core.config import app_settings

app = FastAPI(
    title=app_settings.app_title,
    default_response_class=ORJSONResponse,
)
# app.include_router(base.router, prefix='/api/v1')
app.include_router(base.router)


# @app.on_event('startup')
# async def init_tables():
#     from db.db import engine
#     from models import Base
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(
        f'redis://{app_settings.redis_host}:{app_settings.redis_port}',
        encoding='utf8',
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
        reload=True,
        log_config=logger.LOGGING
    )
