import os
from dotenv import load_dotenv
import regex
from atproto import Client, models

APP_ENV = os.getenv('APP_ENV', 'test')
MAX_BLUESKY_CAPTION_GRAPHEMES = 300

if APP_ENV == 'prod':
    load_dotenv('.env', override=True)
else:
    load_dotenv('.env.test', override=True)

def get_client():
    client = Client()
    client.login(os.getenv('BLUESKY_USERNAME'), 
                 os.getenv('BLUESKY_APP_PASSWORD'))
    return client

def grapheme_len(text):
    """
    Returns grapheme count for text string.
    A grapheme a piece of text percieved by human to be a single character.
    """
    return len(regex.findall(r'\X', text))

def img_post(pillow_img, 
             image_bytes,
             caption='', 
             alt_text='', 
             aspect_ratio='fit', 
             client=None):
    """
    Posts an image to Bluesky with an optional caption, alt text, and aspect ratio.

    If `aspect_ratio` is set to 'fit' (default), the dimensions are inferred from the
    provided Pillow image. Otherwise, a custom (height, width) tuple can be used.

    Args:
        pillow_img (PIL.Image.Image): The Pillow image object for determining aspect ratio.
        image_bytes (bytes): The raw image data to upload (PNG or JPEG).
        caption (str, optional): Text to accompany the image. Defaults to an empty string.
        alt_text (str, optional): Alt text for accessibility. Defaults to an empty string.
        aspect_ratio (Union[str, Tuple[int, int]], optional): 'fit' to use image dimensions, or
            a (height, width) tuple for manual aspect ratio. Defaults to 'fit'.
        client (atproto.Client, optional): An authenticated Bluesky client. If None, a default client is used.

    Returns:
        atproto.models.AppBskyFeedPost.Response: The response from the Bluesky post request.
    """
    if grapheme_len(caption) > MAX_BLUESKY_CAPTION_GRAPHEMES:
        raise ValueError(f"Caption exceeds {MAX_BLUESKY_CAPTION_GRAPHEMES} grapheme limit imposed by Bluesky API.")

    if not client:
        client = get_client()
    
    if aspect_ratio == 'fit':
        ar_for_api = models.AppBskyEmbedDefs.AspectRatio(
            height=pillow_img.height,
            width=pillow_img.width
        )
    else:
        ar_for_api = models.AppBskyEmbedDefs.AspectRatio(
            height=aspect_ratio[0],
            width=aspect_ratio[1]
        )

    return client.send_image(
        text=caption,
        image=image_bytes,
        image_alt=alt_text,
        image_aspect_ratio=ar_for_api
    )
