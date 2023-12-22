import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy import inspect

from api.v1 import base
from core import config, logger
from db.db import engine
from models import Base

app = FastAPI(
    title=config.app_settings.app_title,
    default_response_class=ORJSONResponse,
)
app.include_router(base.router, prefix='/api/v1')


@app.on_event('startup')
def setup():
    print("Creating db tables...")
    Base.metadata.create_all(bind=engine)
    inspection = inspect(engine)
    print(f"Created {len(inspection.get_table_names())} "
          f"tables: {inspection.get_table_names()}")


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_settings.project_host,
        port=config.app_settings.project_port,
        reload=True,
        log_config=logger.LOGGING
    )
