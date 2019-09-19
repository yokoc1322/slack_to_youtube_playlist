import json
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from pprint import pprint

import requests

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
