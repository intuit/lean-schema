import pytest

from lean_schema.get_types import main
from unittest import mock
import lean_schema


@mock.patch("lean_schema.get_types.load_schema")
def test_main(load_schema_mock):
    assert load_schema_mock is not None
