FROM python:3.7-slim

ADD slack_to_youtube_playlist slack_to_youtube_playlist
WORKDIR slack_to_youtube_playlist
RUN pip install -r requirements.txt

CMD ["python", "slack_bot.py"]
