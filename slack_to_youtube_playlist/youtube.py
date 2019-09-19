import os
import json
import logging
from urllib.parse import urlparse, parse_qs

import requests


class Youtube():
    def __init__(self, client_id, client_secret, refresh_token):
        logging.basicConfig(level='INFO')
        self.logger = logging.getLogger(self.__class__.__name__)

        self.access_token = ''
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

        self.refresh_access_token()

    def refresh_access_token(self):
        TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

        res = requests.post(TOKEN_URL, params={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        })

        res.raise_for_status()

        self.access_token = json.loads(res.content.decode())['access_token']

    def logger_response(self, res):
        self.logger.info(res.status_code)
        self.logger.info(res.content.decode())

    def get_youtube_resource(self, url, params={}, retry_token_expires=True):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        res = requests.get(url, headers=headers, params=params)
        self.logger_response(res)

        if res.status_code == 401 and retry_token_expires:
            self.refresh_access_token()
            res = self.get_youtube_resource(url, params, False)

        return res

    def post_youtube_resource(self, url, params={}, json_data={}, retry_token_expires=True):
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        res = requests.post(url, headers=headers,
                            params=params, json=json_data)
        self.logger_response(res)

        if res.status_code == 401 and retry_token_expires:
            self.refresh_access_token()
            res = self.post_youtube_resource(url, params, json_data, False)

        return res

    def insert_playlists_items(self, playlist_id, video_id):
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
        res = self.post_youtube_resource(PLAYLIST_ITEMS_URL, params, data)
        self.logger.info(res.status_code)
        self.logger.info(res.content)

    def get_video_id(self, url_str):
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
            raise ValueError(
                "Not support netloc of the url: {}".format(url_str))
        return video_id

    def insert_video_to_playlist_by_url(self, playlist_id, url):
        try:
            video_id = self.get_video_id(url)
        except ValueError as e:
            self.logger.info(e)
            return
        self.insert_playlists_items(playlist_id, video_id)


if __name__ == '__main__':
    client_id = os.environ['YOUTUBE_CLIENT_ID']
    client_secret = os.environ['YOUTUBE_CLIENT_SECRET']
    refresh_token = os.environ['YOUTUBE_REFRESH_TOKEN']
    playlist_id = os.environ['YOUTUBE_PLAYLIST_ID']

    youtube = Youtube(client_id, client_secret, refresh_token)

    # url = 'https://www.youtube.com/watch?v=gmRy-JW5aps'
    url = 'https://www.youtube.com/watch?v=SX_ViT4Ra7k'

    youtube.insert_video_to_playlist_by_url(playlist_id, url)
