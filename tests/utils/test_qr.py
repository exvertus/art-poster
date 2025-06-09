import pytest

from tests.utils.qr import decode_qr_from_bytes, generate_random_qr

def test_decode_qr_fails_on_non_qr_image(dummy_image):
    """
    Unit test that tests QR code test logic. 
    Protects against silent false-positives.
    """
    image_bytes = dummy_image["bytes"]

    with pytest.raises(ValueError, match="QR image failed decoding"):
        decode_qr_from_bytes(image_bytes)

def test_qr_round_trip_success():
    """A randomly generated QR code's seed should match its decoded number."""
    qr = generate_random_qr()
    original = qr["number"]
    decoded = decode_qr_from_bytes(qr["bytes"])
    assert decoded == original
