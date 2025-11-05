# tests/test_utils_logger.py
"""
Tests for logging utilities.

These tests verify the logger configuration and functionality.
"""
def test_logger_module_import():
    """Test that logger module can be imported."""
    from src.utils import logger
    
    assert logger is not None


def test_get_logger_function():
    """Test that get_logger function exists and works."""
    from src.utils.logger import get_logger
    
    # Get a logger instance
    log = get_logger(__name__)
    
    assert log is not None
    assert hasattr(log, "info")
    assert hasattr(log, "error")
    assert hasattr(log, "warning")
    assert hasattr(log, "debug")


def test_logger_basic_operations():
    """Test basic logger operations."""
    from src.utils.logger import get_logger
    
    log = get_logger("test_logger")
    
    # These should not raise exceptions
    log.info("Test info message")
    log.debug("Test debug message")
    log.warning("Test warning message")
    
    # Logger should be callable
    assert callable(log.info)
    assert callable(log.error)


def test_logger_with_context():
    """Test logger with structured context."""
    from src.utils.logger import get_logger
    
    log = get_logger("test_context_logger")
    
    # Structlog supports context
    log.info("Test with context", symbol="AAPL", price=150.0)
    
    # Should not raise exceptions
    assert True


def test_multiple_loggers():
    """Test creating multiple logger instances."""
    from src.utils.logger import get_logger
    
    log1 = get_logger("logger1")
    log2 = get_logger("logger2")
    
    assert log1 is not None
    assert log2 is not None
    
    # They should work independently
    log1.info("Message from logger1")
    log2.info("Message from logger2")
