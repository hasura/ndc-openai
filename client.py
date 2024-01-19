from openai import AsyncClient
from models import Configuration


def get_client(config: Configuration):
    return AsyncClient(
        organization=config.organization,
        api_key=config.api_key
    )
