"""
Unit Tests for Trading Strategies
"""
import pytest
from strategies.strategy1 import Strategy1
from strategies.strategy2 import Strategy2
from config import Config

@pytest.fixture
def config():
    return Config()

def test_strategy1_initialization(config):
    strategy = Strategy1(config)
    assert strategy is not None
    
def test_strategy2_initialization(config):
    strategy = Strategy2(config)
    assert strategy is not None