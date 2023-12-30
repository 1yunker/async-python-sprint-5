import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import base
from core import config, logger

# from db.db import engine
# from models import Base

app = FastAPI(
    title=config.app_settings.app_title,
    default_response_class=ORJSONResponse,
)
# app.include_router(base.router, prefix='/api/v1')
app.include_router(base.router)


# @app.on_event('startup')
# async def init_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_settings.project_host,
        port=config.app_settings.project_port,
        reload=True,
        log_config=logger.LOGGING
    )
