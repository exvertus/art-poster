import os
from dotenv import load_dotenv
from atproto import Client, models

APP_ENV = os.getenv('APP_ENV', 'test')

if APP_ENV == 'prod':
    load_dotenv('.env', override=True)
else:
    load_dotenv('.env.test', override=True)

def get_client():
    client = Client()
    client.login(os.getenv('BLUESKY_USERNAME'), 
                 os.getenv('BLUESKY_APP_PASSWORD'))
    return client

def img_post(pillow_img, 
             image_bytes,
             caption='', 
             alt_text='', 
             aspect_ratio='fit', 
             client=None):
    """
    TODO: Fill this in.
    """
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
