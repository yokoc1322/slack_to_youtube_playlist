import json
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from pprint import pprint

import requests

filename = Path(__file__).name.split('.')[0]

logging.basicConfig(level='INFO')
logger = logging.getLogger(filename)

OAUTH_PARAM_FILE = './secrets/client_secret.json'
OAUTH_PARAMS = None
with open(OAUTH_PARAM_FILE, mode='r') as f:
    OAUTH_PARAMS = json.loads(f.read())['installed']


def get_tmp_code():
    OAUTH_ACCEPT_HTML_FILE = './public/auth.html'
    OAUTH_URL = 'https://accounts.google.com/o/oauth2/auth'

    send_oauth_params = {
        'client_id': OAUTH_PARAMS['client_id'],
        # 'redirect_uri': urllib.parse.quote(OAUTH_PARAMS['redirect_uris'][1]),
        'redirect_uri': OAUTH_PARAMS['redirect_uris'][0],
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/youtube',
        'access_type': 'offline'
    }

    res = requests.get(OAUTH_URL, params=send_oauth_params)
    with open(OAUTH_ACCEPT_HTML_FILE, 'w') as f:
        f.write(res.content.decode())


def get_access_token():
    TEMP_TOKEN_FILE = './secrets/tmp_token'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    token = ''
    with open(TEMP_TOKEN_FILE, 'r') as f:
        token = f.read().strip()
    send_data = {
        'code': token,
        'client_id': OAUTH_PARAMS['client_id'],
        'client_secret': OAUTH_PARAMS['client_secret'],
        'redirect_uri': OAUTH_PARAMS['redirect_uris'][0] + '',
        'grant_type': 'authorization_code',
        'access_type': 'offline'
    }
    res = requests.post(TOKEN_URL, data=send_data)

    ACCESS_TOKEN_FILE = './secrets/access_token.json'
    with open(ACCESS_TOKEN_FILE, 'w') as f:
        f.write(json.dumps(res.content.decode()))


def reflesh_access_token():
    ACCESS_TOKEN_FILE = './secrets/access_token.json'

    access_token_data = {}
    with open(ACCESS_TOKEN_FILE, 'r') as f:
        access_token_data = json.loads(f.read())
    refresh_token = access_token_data['refresh_token']
    scope = access_token_data['scope']

    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    res = requests.post(TOKEN_URL, params={
        'client_id': OAUTH_PARAMS['client_id'],
        'client_secret': OAUTH_PARAMS['client_secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    })

    res.raise_for_status()

    new_access_token_data = json.loads(res.content.decode())
    new_access_token_data['refresh_token'] = refresh_token
    new_access_token_data['scope'] = scope

    ACCESS_TOKEN_FILE = './secrets/access_token.json'
    with open(ACCESS_TOKEN_FILE, 'w') as f:
        f.write(json.dumps(new_access_token_data))


def logger_response(res):
    logger.info(res.status_code)
    logger.info(res.content.decode())


def get_youtube_resource(url, params={}):
    ACCESS_TOKEN_FILE = './secrets/access_token.json'
    data = {}
    with open(ACCESS_TOKEN_FILE, 'r') as f:
        data = json.loads(f.read())
    headers = {'Authorization': 'Bearer {}'.format(data['access_token'])}
    res = requests.get(url, headers=headers, params=params)
    logger_response(res)
    return res


def post_youtube_resource(url, params={}, json_data={}):
    ACCESS_TOKEN_FILE = './secrets/access_token.json'
    data = {}
    with open(ACCESS_TOKEN_FILE, 'r') as f:
        data = json.loads(f.read())
    headers = {'Authorization': 'Bearer {}'.format(data['access_token'])}
    res = requests.post(url, headers=headers, params=params, json=json_data)
    logger_response(res)
    return res


def get_playlists_items(playlist_id):
    PLAYLIST_ITEMS_URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet',
        'playlistId': playlist_id
    }
    res = get_youtube_resource(PLAYLIST_ITEMS_URL, params)
    # print(res.status_code)
    # pprint(json.loads(res.content))


def insert_playlists_items(playlist_id, video_id):
    PLAYLIST_ITEMS_URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet',
    }
    data = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            },
        },
    }
    res = post_youtube_resource(PLAYLIST_ITEMS_URL, params, data)
    # print(res.status_code)
    # pprint(json.loads(res.content))


def get_playlist_id():
    with open('./secrets/playlist_id', 'r') as f:
        return f.read().strip()


def get_video_id(url_str):
    url = urlparse(url_str)
    pprint(url)
    video_id = ''
    if url.netloc == 'www.youtube.com':
        query = parse_qs(url.query)
        if 'v' not in query:
            raise ValueError(
                "Cannot find 'v' query in the url: {}".format(url_str))
        video_id = query['v'][0]
    elif url.netloc == 'youtu.be':
        try:
            video_id = url.path.split('/')[1]
        except IndexError:
            raise ValueError(
                "Cannot find video_id in path in the url {}".format(url_str))
    else:
        raise ValueError("Not support netloc of the url: {}".format(url_str))
    return video_id

    # res = requests.get(url)
    # pprint(res.headers)


def insert_video_to_playlist_by_url(url):
    video_id = get_video_id(url)
    insert_playlists_items(get_playlist_id(), video_id)


if __name__ == '__main__':
    # reflesh_access_token()
    # get_playlists_items(get_playlist_id())
    insert_video_to_playlist_by_url()
