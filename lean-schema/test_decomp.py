"""
Tests for Intuit Schema Decomp aka LeanSchema

"""

__author__ = "prussell"

import pytest
import decomp
import argparse
import json
from unittest.mock import patch


def test_check_input_object_depth_level():
    # Garbage non-integer
    with pytest.raises(argparse.ArgumentTypeError):
        decomp.check_input_object_depth_level("0xdeadbeef")

    with pytest.raises(argparse.ArgumentTypeError):
        decomp.check_input_object_depth_level(-1)

    for I in [0, 1, 2, 22, 3000]:
        E = I
        R = decomp.check_input_object_depth_level(str(I))


def test_get_types_from_file():
    G = decomp.mk_adj_from_graphql_schema(decomp.load_schema("test/schema.json"))
    types_file = {"types": ["Network_Contact", "Entity"], "domains": ["risk"]}

    R = decomp.get_types_from_file(G, types_file)
    assert "Network_Contact" in R
    assert "Entity" in R
    risk_types = [tkey for tkey in G if tkey.startswith("Risk")]
    for tkey in risk_types:
        assert tkey in R


def test_get_types_from_file_with_depth():
    G = decomp.mk_adj_from_graphql_schema(decomp.load_schema("test/schema.json"))
    types_file = {"types": [{"CreateSales_SaleInput": {"depth": 2}}]}

    R = decomp.get_types_from_file(G, types_file)
    assert "CreateSales_SaleInput" in R
    for reftype in [
        "Attachment_AttachmentInput",
        "Common_CustomFieldValueInput",
        "Common_ExternalIdInput",
        "Common_MetadataInput",
        "Network_ContactInput",
        "Sales_Definitions_GratuityTraitInput",
        "Sales_Definitions_PaymentTraitInput",
        "Sales_SaleInput",
        "Sales_SaleLineInput",
        "Transactions_Definitions_BalanceTraitInput",
        "Transactions_Definitions_CurrencyInfoInput",
        "Transactions_Definitions_DiscountTraitInput",
        "Transactions_Definitions_ShippingTraitInput",
        "Transactions_Definitions_TaxTraitInput",
        "Transactions_Definitions_TransactionLinksInput",
    ]:
        assert reftype in R


def test_all_scalar_types():
    tree = {
        "A": [{"kind": "scalar", "name": "Int"}, {"kind": "scalar", "name": "Float"}],
        "B": {"kind": "ListType", "bloop": True},
        "C": [
            {"kind": "SCALAR", "name": "Bool"},
            {"kind": "ObjectType", "name": "Foo"},
        ],
    }
    scalars = decomp.all_scalar_types(tree)
    for etype in ["Int", "Float", "Bool"]:
        assert etype in scalars
    assert "Foo" not in scalars
    assert "ListType" not in scalars
    assert "ObjectType" not in scalars


@patch("sys.stdin")
@patch("builtins.print")
def test_main_happy_path(print_mock, stdin_mock):
    stdin_mock.fileno = lambda: 2
    stdin_mock.read = lambda: json.dumps({"types": ["Entity"]})
    args = ["test/schema.json", "--types-file=test/types.yaml", "--log-level=DEBUG"]
    subschema = decomp.main(args)
    subgraph = decomp.mk_adj_from_graphql_schema(subschema)
    assert print_mock.call_count == 1
    assert "CreateSales_SaleInput" in subgraph
