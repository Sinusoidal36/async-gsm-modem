import pytest

@pytest.fixture
def urc_codes():
    return [(b'+CMTI', 1), (b'+CMT', 2)]