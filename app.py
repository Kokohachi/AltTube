import locale
import os

import dotenv
import jaconv
import num2words
from apiclient.discovery import build
from apiclient.errors import HttpError
from flask import Flask, render_template, request
from oauth2client.tools import argparser

locale.setlocale(locale.LC_ALL, '')

app = Flask(__name__)
dotenv.load_dotenv()

YOUTUBE_DEVELOPER_KEY = os.getenv("YOUTUBE_DEVELOPER_KEY")
YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION")

youtube = build(
YOUTUBE_API_SERVICE_NAME,
YOUTUBE_API_VERSION,
developerKey=YOUTUBE_DEVELOPER_KEY
    )

def youtube_search(query):
    yt_query = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=25
        )
    response = yt_query.execute()
    return response

def get_video_info(video_id):
    video_info = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
        ).execute()
    return video_info

def get_channel_info(channel_id):
    channel_info = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
        ).execute()
    return channel_info

@app.route("/")
def index():
    if request.args.get('keyword'):
        keyword = request.args.get('keyword')
    else:
        keyword = "ぼっちざろっく"
    videos = youtube_search(keyword)
    video_titles = []
    video_thumbnails = []
    video_ids = []
    video_channels = []
    video_channel_thumbnails = []
    video_seen = []
    for video in videos['items']:
        if video['id']['kind'] == 'youtube#video':
            video_titles.append(video['snippet']['title'])
            video_thumbnails.append(video['snippet']['thumbnails']['high']['url'])
            video_ids.append(video['id']['videoId'])
            video_channels.append(video['snippet']['channelTitle'])
            video_channel_thumbnails.append(get_channel_info(video['snippet']['channelId'])['items'][0]['snippet']['thumbnails']['high']['url'])
            video_seen.append(f"{int((get_video_info(video['id']['videoId'])['items'][0]['statistics']['viewCount'])):n}")

    video_datas = zip(video_titles, video_thumbnails, video_ids, video_channels, video_channel_thumbnails, video_seen)
    return render_template('index.html', video_datas=video_datas)

@app.route("/video")
def video():
    video_id  = request.args.get('video_id')
    video_title = get_video_info(video_id)['items'][0]['snippet']['title']
    video_desc = get_video_info(video_id)['items'][0]['snippet']['description'].split('\n')
    return render_template('video.html', video_id=video_id , video_title=video_title, video_description=video_desc)


PORT = int(os.getenv("PORT"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)