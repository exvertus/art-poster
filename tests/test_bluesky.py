import pytest
import qrcode
import secrets
from PIL import Image
from io import BytesIO
from qrcode.constants import ERROR_CORRECT_H
from pyzbar.pyzbar import decode

import platforms.bluesky as bluesky

@pytest.fixture
def test_client():
    return bluesky.get_client()

@pytest.fixture
def random_qr_code():
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
    img = Image.open(BytesIO(image_bytes))
    decoded = decode(img)
    if not decoded:
        raise ValueError("QR image failed decoding")
    return decoded[0].data.decode()

@pytest.fixture
def bluesky_post(test_client, random_qr_code):
    post_response = bluesky.img_post(random_qr_code["image"], 
                                     random_qr_code["bytes"], 
                                     caption='This is a test.',
                                     client=test_client)
    post_rkey = post_response.uri.split('/')[-1]

    yield {
        "post_rkey": post_rkey,
        "qr_number": random_qr_code["number"],
        "image_ref": post_response
    }

    test_client.delete_post(post_response.uri)

def test_img_post(test_client, bluesky_post):
    original_qr_num = bluesky_post["qr_number"]

    get_response = test_client.get_post(bluesky_post["post_rkey"])
    response_image = get_response.value.embed.images[0]
    blob_ref = response_image.image.ref.link
    repo = test_client.me.did
    blob_bytes = test_client.com.atproto.sync.get_blob(
        params={"did": repo, "cid": blob_ref}
    )
    decoded_qr_num = decode_qr_from_bytes(blob_bytes)

    assert decoded_qr_num == original_qr_num
