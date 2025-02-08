import pytest

def test_default_config():
    """ Test that default conf raise a value error, some var env are needed
    """
    from api.config import config
    config.POSTGRESQL_URI = None
    with pytest.raises(ValueError):
        config.validate()


def test_config():
    from api.config import config
    config.POSTGRESQL_URI = "sqlite:///:memory:"
    config.validate()

    assert "DEBUG" == config.LOGGER_LEVEL
    assert "sqlite:///:memory:" == config.POSTGRESQL_URI
