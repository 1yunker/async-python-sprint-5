import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

# from api.v1 import base
from core import config, logger

app = FastAPI(
    title=config.app_settings.app_title,
    default_response_class=ORJSONResponse,
)
# app.include_router(base.router, prefix='/api/v1')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_settings.project_host,
        port=config.app_settings.project_port,
        reload=True,
        log_config=logger.LOGGING
    )
