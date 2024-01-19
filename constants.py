from hasura_ndc import ScalarType

SCALAR_TYPES = {
    "Int": ScalarType(**{
        "aggregate_functions": {},
        "comparison_operators": {}
    }),
    "Float": ScalarType(**{
        "aggregate_functions": {},
        "comparison_operators": {}
    }),
    "String": ScalarType(**{
        "aggregate_functions": {},
        "comparison_operators": {}
    }),
    "FileBytes": ScalarType(**{
        "aggregate_functions": {},
        "comparison_operators": {}
    }),
    "JSON": ScalarType(**{
        "aggregate_functions": {},
        "comparison_operators": {}
    })
}
