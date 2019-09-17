import os
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from slack import RTMClient

from youtube import set_secrets, insert_video_to_playlist_by_url

filename = Path(__file__).name.split('.')[0]

logging.basicConfig(level='INFO')
logger = logging.getLogger(filename)


def is_text_url(text):
    ret = urlparse(text)
    if ret.scheme == 'http' or ret.scheme == 'https':
        return True
    return False


@RTMClient.run_on(event='message')
def say_youtube_url(**payload):
    try:
        text = payload['data']['text'][1:-1]
        if is_text_url(text):
            insert_video_to_playlist_by_url(playlist_id, text)
    except KeyError as e:
        logging.warn(e)
    except ValueError as e:
        logging.warn(e)


client_id = os.environ['YOUTUBE_CLIENT_ID']
client_secret = os.environ['YOUTUBE_CLIENT_SECRET']
refresh_token = os.environ['YOUTUBE_REFRESH_TOKEN']
playlist_id = os.environ['YOUTUBE_PLAYLIST_ID']
slack_api_token = os.environ['SLACK_API_TOKEN']

set_secrets(client_id, client_secret, refresh_token)

rtm_client = RTMClient(token=slack_api_token)
rtm_client.start()
