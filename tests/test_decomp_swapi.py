
from lean_schema import decomp

def test_get_types_from_file():
    G = decomp.mk_adj_from_graphql_schema(decomp.load_schema("tests/swapi_schema.json"))
    types_file = {"types": ["Human", "Droid", "Starship"], "domains": []}

    R = decomp.get_types_from_file(G, types_file)
    assert len(R) == 3
    assert "Human" in R
    assert "Droid" in R
    assert "Starship" in R