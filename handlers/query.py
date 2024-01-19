from hasura_ndc import *
from models import Configuration, State


async def query(configuration: Configuration, state: State, query_request: QueryRequest) -> QueryResponse:
    print(configuration)
    print(state)
    print(query_request)
    if query_request.collection == "query_health":
        res: QueryResponse = [
            RowSet(
                aggregates=None,
                rows=[
                    {"__value": "Reporting for duty! 🫡🚀"}
                ]
            )
        ]
        return res
