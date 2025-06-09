import pytest
from PIL import Image
from io import BytesIO

from tests.utils.qr import generate_random_qr

@pytest.fixture
def random_qr_code():
    return generate_random_qr()

@pytest.fixture
def dummy_image():
    img = Image.new('RGB', (100, 100), color='gray')  # plain gray image
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return {
        "image": img,
        "bytes": buf.getvalue()
    }
