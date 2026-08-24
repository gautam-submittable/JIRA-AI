import pytest

from generated_feature import (
    example_function,
)


def test_example_function():
    assert example_function(10) == 10


def test_example_function_none():
    with pytest.raises(ValueError):
        example_function(None)
