from openai import AsyncClient
from pydantic import BaseModel
from typing import Optional


class Configuration(BaseModel):
    api_key: str
    organization: Optional[str] = None


RawConfiguration = Configuration


class State(BaseModel):
    client: AsyncClient

    class Config:
        arbitrary_types_allowed = True
