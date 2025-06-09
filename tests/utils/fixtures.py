import pytest

from tests.utils.qr import generate_random_qr

@pytest.fixture
def random_qr_code():
    return generate_random_qr()
