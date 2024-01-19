from hasura_ndc import *
from models import Configuration
from constants import SCALAR_TYPES
from client import get_client
from typing import Dict, Any, List
import inspect
import re

EXCLUDED_SUB_MEMBERS = ["with_raw_response", "with_streaming_response"]

OPENAI_TYPES = {
    "FileTypes": "FileBytes"
}


def map_type(param):
    param_type = str(param.annotation)

    # Check for traditional Union syntax
    union_match = re.match(r"Union\[(.*)]", param_type)
    if union_match:
        union_members = union_match.group(1).split(', ')
    else:
        # Check for Python 3.10+ Union syntax using |
        if '|' in param_type:
            union_members = param_type.split(' | ')
        else:
            union_members = None

    is_nullable = ("None" in union_members or "NotGiven" in union_members) if union_members else False

    if union_members:
        root_type_identified = False
        root_type = None
        for member in union_members:
            if member == "str" or member.startswith("Literal['") or member.startswith('Literal["'):
                root_type_identified = True
                root_type = "String"
            elif member == "float":
                root_type_identified = True
                root_type = "Float"
            elif member == "int":
                root_type_identified = True
                root_type = "Int"
            elif member in OPENAI_TYPES:
                root_type_identified = True
                root_type = OPENAI_TYPES[member]
            elif member in ["None", "NotGiven"]:
                continue

        if not root_type_identified:
            for member in union_members:
                if member in ["None", "NotGiven"]:
                    continue
                else:
                    pass
                    # print(f"Unidentified member: {member}")
        else:
            if is_nullable:
                return Type(
                    type="nullable",
                    underlying_type=Type(
                        type="named",
                        name=root_type
                    )
                )
            else:
                return Type(
                    type="named",
                    name=root_type
                )
    else:
        root_type_identified = False
        root_type = None
        if param_type == "str" or param_type.startswith("Literal['") or param_type.startswith('Literal["'):
            root_type_identified = True
            root_type = "String"
        elif param_type == "float":
            root_type_identified = True
            root_type = "Float"
        elif param_type == "int":
            root_type_identified = True
            root_type = "Int"
        elif param_type in OPENAI_TYPES:
            root_type_identified = True
            root_type = OPENAI_TYPES[param_type]
        else:
            pass

        if root_type_identified:
            return Type(
                type="named",
                name=root_type
            )

    return None


def create_input_object_type_from_method(object_types: Dict[str, ObjectType], method):
    sig = inspect.signature(method)
    fields = {}
    for param_name, param in sig.parameters.items():
        print(param_name)
        mapped_type = map_type(param)
        if mapped_type is not None:
            fields[param_name] = ObjectField(
                type=mapped_type
            )

    return ObjectType(
        description=f"Input type for {method.__name__}",
        fields=fields
    )


async def recursive_inspect_member(object_types: Dict[str, ObjectType],
                                   member: Any,
                                   path: List[str],
                                   depth: int = 0) -> Type | None:
    def _print(*args):
        print("\t" * (depth + 2) + ",".join([str(a) for a in args]))

    if depth > 10:
        return

    if inspect.ismethod(member[1]):
        root_field = "_".join(path)
        object_type = create_input_object_type_from_method(object_types, member[1])
        object_types[root_field] = object_type
        return Type(
            type="named",
            name=root_field
        )
    elif isinstance(member[1], object):
        root_field = "_".join(path)
        fields = {}
        for sub_member in inspect.getmembers(member[1]):
            sub_member_name = sub_member[0]
            if sub_member_name.startswith("_") or sub_member_name in EXCLUDED_SUB_MEMBERS:
                continue
            path.append(sub_member_name)
            print(root_field)
            underlying_type = await recursive_inspect_member(object_types, sub_member, path, depth + 1)
            print("\n")
            fields[path[-1]] = ObjectField(
                description="",
                type=Type(
                    type="nullable",
                    underlying_type=underlying_type
                )
            )
            path.pop()
        object_types[root_field] = ObjectType(
            description="",
            fields=fields
        )
        return Type(
            type="named",
            name=root_field
        )
    else:
        _print("UNKNOWN!!", member)

    return Type(
        type="named",
        name="Int"
    )


async def get_schema(configuration: Configuration) -> SchemaResponse:
    client = get_client(configuration)
    client_members = inspect.getmembers(client)
    endpoints = [
        "audio",
        "beta",
        "chat",
        "embeddings",
        "fine_tuning",
        "files",
        "images",
        "models",
        "moderations"
    ]

    root_fields = {}
    additional_object_types: Dict[str, ObjectType] = {}
    for member in client_members:
        name = member[0]
        if name in endpoints:
            openai_fields = {}
            child_members = inspect.getmembers(member[1])
            for sub_member in child_members:
                sub_member_name = sub_member[0]
                if sub_member_name.startswith("_") or sub_member_name in EXCLUDED_SUB_MEMBERS:
                    continue
                underlying_type = await recursive_inspect_member(additional_object_types,
                                                                 sub_member,
                                                                 [name, sub_member_name])
                if underlying_type is not None:
                    openai_fields[sub_member_name] = ObjectField(
                        description="",
                        type=Type(
                            type="nullable",
                            underlying_type=underlying_type
                        )
                    )

            additional_object_types[name] = ObjectType(
                description="",
                fields=openai_fields
            )

            root_fields[name] = ObjectField(
                descripotion="",
                type=Type(
                    type="nullable",
                    underlying_type=Type(
                        type="named",
                        name=name
                    )
                )
            )

    object_types: Dict[str, ObjectType] = {
        "openai": ObjectType(
            description="OpenAI Root",
            fields=root_fields
        ),
        **additional_object_types
    }

    functions = [
        FunctionInfo(
            arguments={},
            name="query_health",
            description="OpenAI HealthCheck",
            result_type={
                'type': "named",
                'name': "JSON"
            }
        )
    ]

    procedures = [
        ProcedureInfo(
            arguments={},
            name="mutation_health",
            description="OpenAI HealthCheck",
            result_type={
                'type': "named",
                'name': "JSON"
            }
        ),
        ProcedureInfo(
            arguments={
                "input": ArgumentInfo(
                    description="The root argument",
                    type=Type(
                        type="named",
                        name="openai"
                    )
                )
            },
            name="openai",
            description="OpenAI Endpoint",
            result_type={
                'type': "named",
                'name': "JSON"
            }
        )
    ]

    schema_response = SchemaResponse(
        scalar_types=SCALAR_TYPES,
        functions=functions,
        procedures=procedures,
        object_types=object_types,
        collections=[]
    )

    return schema_response
