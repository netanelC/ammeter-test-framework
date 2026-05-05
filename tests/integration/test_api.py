import pytest
import time
from src.testing.test_framework import AmmeterTestFramework

# Run automatically before any tests to start the emulators
@pytest.fixture(scope="session", autouse=True)
def ammeter_emulators():
    """Starts the ammeter emulators in the background for integration tests."""
    from main import start_emulators
    start_emulators()
    yield
    # Daemon threads will terminate automatically when the pytest session completes

@pytest.fixture
def framework():
    return AmmeterTestFramework(config_path="config/config.yaml")

@pytest.fixture
def original_config(framework):
    """Fixture to backup and restore the framework's configuration."""
    orig_cfg = framework.config.get('testing', {}).copy()
    yield
    framework.config['testing'] = orig_cfg

def test_get_single_reading_valid_types(framework):
    for ammeter in ['greenlee', 'entes', 'circutor']:
        val = framework.get_single_reading(ammeter)
        assert isinstance(val, float)
        assert val is not None

def test_get_single_reading_invalid_type(framework):
    with pytest.raises(ValueError, match="Unknown ammeter type"):
        framework.get_single_reading("unknown")

def test_run_test_count_before_duration(framework, original_config):
    # Setup framework to hit count limit before duration limit
    if 'testing' not in framework.config:
        framework.config['testing'] = {'sampling': {}}
    framework.config['testing']['sampling'] = {
        'measurements_count': 2,
        'total_duration_seconds': 5,
        'sampling_frequency_hz': 10
    }
    
    res = framework.run_test('greenlee')
    
    assert res['count'] == 2
    assert res['duration_seconds'] < 2.5

def test_run_test_duration_before_count(framework, original_config):
    # Setup framework to hit duration limit before count limit
    if 'testing' not in framework.config:
        framework.config['testing'] = {'sampling': {}}
    framework.config['testing']['sampling'] = {
        'measurements_count': 10,
        'total_duration_seconds': 0.5,
        'sampling_frequency_hz': 10
    }
    
    res = framework.run_test('greenlee')
    
    assert res['count'] < 10
    assert res['duration_seconds'] >= 0.5
    assert res['duration_seconds'] < 1.0

def test_run_test_both_null_raises_value_error(framework, original_config):
    # Setup framework with missing parameters
    if 'testing' not in framework.config:
        framework.config['testing'] = {'sampling': {}}
    framework.config['testing']['sampling'] = {
        'measurements_count': 'NULL',
        'total_duration_seconds': 'NULL',
        'sampling_frequency_hz': 10
    }
    
    with pytest.raises(ValueError, match="Both measurements_count and total_duration_seconds are missing or NULL"):
        framework.run_test('greenlee')