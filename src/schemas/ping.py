from pydantic import BaseModel


class Ping(BaseModel):
    db: float | str
    cache: float | str
