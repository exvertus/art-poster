import pytest
from tests.utils.qr import decode_qr_from_bytes

import platforms.bluesky as bluesky

@pytest.fixture
def test_client():
    return bluesky.get_client()

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

# Test TODO list:
# - Empty caption and alt text
# - Custom aspect ratio
# - Invalid aspect ratio
# - Non-QR code image fails decoding (testing test logic)
# - image size beyond limits
# - character amount beyond limits
# - Multiple posts in succession
# - non-ASCII character support
# - Client auth error handled gracefully
# - Missing/truncated bytes
