import os
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from slack import RTMClient

from youtube import Youtube

filename = Path(__file__).name.split('.')[0]
logging.basicConfig(level='INFO')
logger = logging.getLogger(filename)

client_id = os.environ['YOUTUBE_CLIENT_ID']
client_secret = os.environ['YOUTUBE_CLIENT_SECRET']
refresh_token = os.environ['YOUTUBE_REFRESH_TOKEN']
playlist_id = os.environ['YOUTUBE_PLAYLIST_ID']
slack_api_token = os.environ['SLACK_API_TOKEN']

youtube = Youtube(client_id, client_secret, refresh_token)


def is_text_url(text):
    ret = urlparse(text)
    if ret.scheme == 'http' or ret.scheme == 'https':
        return True
    return False


@RTMClient.run_on(event='message')
def posted_youtube_url(**payload):
    try:
        text = payload['data']['text'][1:-1]
        if is_text_url(text):
            youtube.insert_video_to_playlist_by_url(playlist_id, text)
    except KeyError as e:
        logger.warning(e)
    except ValueError as e:
        logger.warning(e)


rtm_client = RTMClient(token=slack_api_token)
rtm_client.start()
