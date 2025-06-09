import qrcode
import secrets
from PIL import Image
from io import BytesIO
from qrcode.constants import ERROR_CORRECT_H
from pyzbar.pyzbar import decode

def generate_random_qr():
    """Create an in-memory qr-code image from a random number."""
    test_number = str(secrets.randbits(64))
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(test_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return {
        "number": test_number,
        "image": Image.open(buf),
        "bytes": buf.getvalue()
    }

def decode_qr_from_bytes(image_bytes):
    """Decode a QR's image-bytes back to a number value."""
    img = Image.open(BytesIO(image_bytes))
    decoded = decode(img)
    if not decoded:
        raise ValueError("QR image failed decoding")
    return decoded[0].data.decode()
