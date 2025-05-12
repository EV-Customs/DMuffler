from logging_utils import log_info, log_warning, log_error

def test_log_info():
    log_info("Test info message")
    assert True

def test_log_warning():
    log_warning("Test warning message")
    assert True

def test_log_error():
    log_error("Test error message")
    assert True
