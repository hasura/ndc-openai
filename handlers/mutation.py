import inspect

from hasura_ndc import *
from models import *


async def mutation(configuration: Configuration, state: State, mutation_request: MutationRequest) -> MutationResponse:
    print(configuration)
    print(state)
    print(state.client)
    print(state.client.chat.completions.create)
    # Instrospect this to get what it's arguments are?
    # We need to
    returning = [{"__value": None}]
    for op in mutation_request.operations:
        if op.type == 'procedure':
            if op.name == "health":
                returning = [{"__value": "Reporting for duty! 🫡🚀"}]
            elif op.name == "openai":
                print("OPENAI")
                returning = [{"__value": "OPENAI"}]
            else:
                raise NotImplemented("This is not implemented")

    response = MutationResponse(
        operation_results=[
            MutationOperationResults(
                affected_rows=len(returning),
                returning=returning
            )
        ]
    )
    return response
