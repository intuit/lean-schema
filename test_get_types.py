import pytest

from lean_schema.get_types import main
from unittest import mock
import lean_schema


@mock.patch("lean_schema.get_types.get_schema")
def test_main(get_schema_mock):
    assert get_schema_mock is not None
