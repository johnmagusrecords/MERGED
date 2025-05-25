import pytest
from example import greet

def test_greet():
    assert greet("World") == "Hello, World"
