from lean_schema import decomp
from unittest import mock
import json
import os

if os.path.exists("tests/swapi_schema.json"):
    SWAPI_SCHEMA_PATH = "tests/swapi_schema.json"
elif os.path.exists("swapi_schema.json"):
    SWAPI_SCHEMA_PATH = "swapi_schema.json"
else:
    raise FileNotFoundError(
        "SWAPI Schema File not found in local directory or ./tests!"
    )


def test_get_types_from_file():
    G = decomp.mk_graph_from_schema(decomp.load_schema(SWAPI_SCHEMA_PATH))
    types_file = {"types": ["Human", "Droid", "Starship"], "domains": []}

    R = decomp.get_types_from_file(G, types_file)
    assert len(R) == 3
    assert "Human" in R
    assert "Droid" in R
    assert "Starship" in R


@mock.patch("sys.stdin")
@mock.patch("builtins.print")
def test_main(print_mock, stdin_mock):
    stdin_mock.fileno = lambda: 2
    stdin_mock.read = lambda: json.dumps({"types": ["Human"]})
    args = [SWAPI_SCHEMA_PATH, "--log-level=DEBUG"]
    subschema = decomp.main(args)
    subgraph = decomp.mk_graph_from_schema(subschema)
    assert print_mock.call_count == 1
    assert "Human" in subgraph
