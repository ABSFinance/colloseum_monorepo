"""
Shared test fixtures for optimizer tests
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta

@pytest.fixture
def sample_market_data():
    """Create sample market data for testing"""
    dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
    return {
        "1000": pd.DataFrame({
            'created_at': dates,
            'return': [0.01, 0.02, 0.015, 0.03, 0.02]  # 1%, 2%, 1.5%, 3%, 2%
        }),
        "1001": pd.DataFrame({
            'created_at': dates,
            'return': [0.02, 0.01, 0.03, 0.02, 0.015]  # 2%, 1%, 3%, 2%, 1.5%
        }),
        "1010": pd.DataFrame({
            'created_at': dates,
            'return': [0.015, 0.025, 0.02, 0.015, 0.025]  # 1.5%, 2.5%, 2%, 1.5%, 2.5%
        })
    }

@pytest.fixture
def sample_vault_info():
    """Create sample vault info for testing"""
    return {
        'pool_id': 'vault_1',
        'strategy': 'min_risk',
        'allowed_pools': ['1000', '1010'],
        'adaptors': ['adaptor1', 'adaptor2'],
        'weights': [0.6, 0.4]
    }