from hasura_ndc import *
from typing import Optional, Dict
from models import RawConfiguration, Configuration, State
from handlers.get_schema import get_schema
from handlers.update_configuration import update_configuration
from handlers.query import query
from handlers.mutation import mutation
from client import get_client


class RootConnector(Connector[RawConfiguration, Configuration, State]):

    def __init__(self):
        super().__init__(RawConfiguration, Configuration, State)

    async def validate_raw_configuration(self,
                                         raw_configuration: RawConfiguration
                                         ) -> Configuration:
        return Configuration(**raw_configuration.model_dump())

    async def try_init_state(self, configuration: Configuration, metrics: Any) -> State:
        client = get_client(configuration)
        return State(
            client=client
        )

    async def get_capabilities(self, configuration: Configuration) -> CapabilitiesResponse:
        return CapabilitiesResponse(
            versions="^0.1.0",
            capabilities=Capabilities(
                query=QueryCapabilities(
                    aggregates=LeafCapability(),
                    variables=LeafCapability()
                ),
                explain=LeafCapability(),
                relationships=RelationshipCapabilities(
                    relation_comparisons=LeafCapability(),
                    order_by_aggregate=LeafCapability()
                )
            )
        )

    async def update_configuration(self,
                                   raw_configuration: RawConfiguration) -> RawConfiguration:
        return await update_configuration(raw_configuration)

    async def get_schema(self,
                         configuration: Configuration) -> SchemaResponse:
        return await get_schema(configuration)

    async def explain(self,
                      configuration: Configuration,
                      state: State,
                      request: QueryRequest) -> ExplainResponse:
        raise NotImplemented

    async def query(self, configuration: Configuration, state: State, request: QueryRequest) -> QueryResponse:
        return await query(configuration, state, request)

    async def mutation(self,
                       configuration: Configuration,
                       state: State,
                       request: MutationRequest) -> MutationResponse:
        return await mutation(configuration, state, request)

    # SERVER
    def get_raw_configuration_schema(self) -> Dict[str, Any]:
        return RawConfiguration.model_json_schema()

    # SERVER
    def make_empty_configuration(self) -> RawConfiguration:
        return RawConfiguration(
            credentials={
                "organization": "",
                "api_key": ""
            }
        )

    async def fetch_metrics(self,
                            configuration: Configuration,
                            state: State) -> Optional[None]:
        pass

    async def health_check(self,
                           configuration: Configuration,
                           state: State) -> Optional[None]:
        pass


if __name__ == "__main__":
    c = RootConnector()
    start(c)
