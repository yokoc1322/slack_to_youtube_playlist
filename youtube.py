import os
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

filename = Path(__file__).name.split('.')[0]

logging.basicConfig(level='INFO')
logger = logging.getLogger(filename)

# TODO: グローバルで持たないようにする
secrets_dict = {
    'access_token': None,
    'client_id': None,
    'client_secret': None,
    'refresh_token': None
}


def set_secrets(client_id, client_secret, refresh_token):
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    res = requests.post(TOKEN_URL, params={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    })

    global secrets_dict

    res.raise_for_status()
    access_token = json.loads(res.content.decode())['access_token']
    secrets_dict = {
        'access_token': access_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }


def refresh_secrets():
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    global secrets_dict

    res = requests.post(TOKEN_URL, params={
        'client_id': secrets_dict['client_id'],
        'client_secret': secrets_dict['client_secret'],
        'refresh_token': secrets_dict['refresh_token'],
        'grant_type': 'refresh_token'
    })

    res.raise_for_status()
    access_token = json.loads(res.content.decode())['access_token']
    secrets_dict['access_token'] = access_token


def logger_response(res):
    logger.info(res.status_code)
    logger.info(res.content.decode())


def get_youtube_resource(url, params={}):
    global secrets_dict
    headers = {'Authorization': 'Bearer {}'.format(
        secrets_dict['access_token'])}
    res = requests.get(url, headers=headers, params=params)
    logger_response(res)
    # TODO: リファクタリング
    if res.status_code == 401:
        refresh_secrets()
        headers = {'Authorization': 'Bearer {}'.format(
            secrets_dict['access_token'])}
        res = requests.get(url, headers=headers, params=params)
        logger_response(res)
    return res


def post_youtube_resource(url, params={}, json_data={}):
    global secrets_dict
    headers = {'Authorization': 'Bearer {}'.format(
        secrets_dict['access_token'])}
    res = requests.post(url, headers=headers, params=params, json=json_data)
    logger_response(res)
    # TODO: リファクタリング
    if res.status_code == 401:
        refresh_secrets()
        headers = {'Authorization': 'Bearer {}'.format(
            secrets_dict['access_token'])}
        res = requests.post(url, headers=headers,
                            params=params, json=json_data)
        logger_response(res)
    return res


# def get_playlists_items(access_token, playlist_id):
#     PLAYLIST_ITEMS_URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
#     params = {
#         'part': 'snippet',
#         'playlistId': playlist_id
#     }
#     res = get_youtube_resource(PLAYLIST_ITEMS_URL, params)


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
    logger.info(res.status_code)
    logger.info(res.content)


def get_video_id(url_str):
    url = urlparse(url_str)
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


def insert_video_to_playlist_by_url(playlist_id, url):
    try:
        video_id = get_video_id(url)
    except ValueError as e:
        logger.info(e)
        return
    insert_playlists_items(playlist_id, video_id)


if __name__ == '__main__':
    client_id = os.environ['YOUTUBE_CLIENT_ID']
    client_secret = os.environ['YOUTUBE_CLIENT_SECRET']
    refresh_token = os.environ['YOUTUBE_REFRESH_TOKEN']
    playlist_id = os.environ['YOUTUBE_PLAYLIST_ID']

    set_secrets(client_id, client_secret, refresh_token)

    # url = 'https://www.youtube.com/watch?v=gmRy-JW5aps'
    url = 'https://www.youtube.com/watch?v=SX_ViT4Ra7k'
    insert_video_to_playlist_by_url(playlist_id, url)
