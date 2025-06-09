import pytest
from tests.utils.qr import decode_qr_from_bytes
from atproto_client.exceptions import BadRequestError
from atproto import models

import platforms.bluesky as bluesky

@pytest.fixture(scope="session")
def test_client():
    client = bluesky.get_client()
    return client

@pytest.fixture
def caption_text():
    return "This is a #test 🔥🚀 Привет 🌍 こんにちは مرحبا"

@pytest.fixture
def alt_text():
    return "Test QR code"

@pytest.fixture
def bluesky_post_happy(test_client, caption_text, random_qr_code, alt_text):
    post_response = bluesky.img_post(random_qr_code["image"], 
                                     random_qr_code["bytes"], 
                                     caption=caption_text,
                                     alt_text=alt_text,
                                     client=test_client)
    post_rkey = post_response.uri.split('/')[-1]

    yield {
        "post_rkey": post_rkey,
        "qr_number": random_qr_code["number"],
        "image_ref": post_response
    }

    test_client.delete_post(post_response.uri)

@pytest.mark.slow
@pytest.mark.integration
def test_img_post(test_client, bluesky_post_happy, caption_text, alt_text):
    original_qr_num = bluesky_post_happy["qr_number"]

    get_response = test_client.get_post(bluesky_post_happy["post_rkey"])
    response_image = get_response.value.embed.images[0]
    blob_ref = response_image.image.ref.link
    repo = test_client.me.did
    blob_bytes = test_client.com.atproto.sync.get_blob(
        params={"did": repo, "cid": blob_ref}
    )
    decoded_qr_num = decode_qr_from_bytes(blob_bytes)

    assert get_response.value.text == caption_text
    assert response_image.alt == alt_text
    assert decoded_qr_num == original_qr_num

@pytest.fixture
def caption_too_many():
    return 5 * "Bluesky has a grapheme limit of 300 this fixture exceeds that"

@pytest.fixture
def bluesky_post_too_many(test_client, caption_too_many, dummy_image, alt_text):
    post_response = bluesky.img_post(dummy_image["image"],
                                     dummy_image["bytes"],
                                     caption=caption_too_many,
                                     alt_text=alt_text,
                                     client=test_client)
    post_rkey = post_response.uri.split('/')[-1]

    yield {
        "post_rkey": post_rkey,
        "image_ref": post_response
    }

    test_client.delete_post(post_response.uri)

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.driftdetect
def test_caption_exceeds_character_limit_on_api(test_client, caption_too_many, 
                                                dummy_image, alt_text):
    image = dummy_image["image"]
    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=image.height,
                                                       width=image.width)
    with pytest.raises(BadRequestError):
        test_client.send_image(image=dummy_image["bytes"],
                               text=caption_too_many,
                               image_alt=alt_text,
                               image_aspect_ratio=aspect_ratio)
        
def test_caption_exceeds_character_limit(caption_too_many, dummy_image, alt_text):
    with pytest.raises(ValueError):
        bluesky.img_post(dummy_image["image"],
                         dummy_image["bytes"],
                         caption=caption_too_many,
                         alt_text=alt_text)

@pytest.mark.parametrize("text,expected", [
    ("", 0),
    ("a", 1),
    ("hello", 5),
    ("á", 1),
    ("mañana", 6),
    ("🇺🇸", 1),
    ("👨‍👩‍👧‍👦", 1),
    ("👍🏽", 1),
    ("e\u0301e", 2),
    ("👩‍❤️‍💋‍👩", 1),
    ("👩🏽‍🚒", 1),
    ("🤦🏽‍♂️", 1),
    ("👨‍👨‍👦", 1),
    ("🧑‍🔧🧑‍🔬", 2),
    ("🏳️‍🌈", 1),
])
def test_grapheme_len(text, expected):
    assert bluesky.grapheme_len(text) == expected

# Test TODO list:
# - Empty caption and alt text
# - Custom aspect ratio
# - Invalid aspect ratio
# - image size beyond limits
# - character amount beyond limits
# - Client auth error handled gracefully
# - Missing/truncated bytes
