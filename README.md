# slack_to_youtube_playlist

slack_to_youtube_playlist inserts youtube video posted via slack bot user, to youtube playlist.

## How to Use

### Configure Bot users(used RTM API) in slack

### Configure Youtube Data API

### Run slack_to_youtube_playlist

```bash
docker build -t slack-to-emoji-register .
docker run \
    YOUTUBE_ACCESS_TOKEN='<youtube access token>' \
    YOUTUBE_CLIENT_ID='<youtube client ID>' \
    YOUTUBE_CLIENT_SECRET='<youtube client secret>' \
    YOUTUBE_REFRESH_TOKEN='<youtube refresh token>' \
    YOUTUBE_PLAYLIST_ID='<youtube playlist id>' \
    SLACK_API_TOKEN='<slack api token>' \
    slack-to-emoji-register
```

### Post youtube video url to slack

Insert youtube video to the playlist, if user posts youtube video url to slack channel joined the bot user.
(User must only contains the url in one post)
