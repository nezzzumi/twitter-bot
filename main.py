import os
import re
import time
from datetime import datetime

import requests
import tweepy
from dotenv import load_dotenv

def get_current_song(user: str, api_key: str) -> str:
    response = requests.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={api_key}&format=json')
    response_json = response.json()

    tracks = response_json['recenttracks']['track']

    for track in tracks:
        if '@attr' in track.keys() and track['@attr']['nowplaying']:
            return f'{track["artist"]["#text"]} - {track["name"]}'

load_dotenv()

while True:
    actual_track = get_current_song(os.getenv('LASTFM_USER'), os.getenv('LASTFM_API_KEY'))

    if not actual_track:
        continue

    print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] listening to: '+actual_track)

    auth = tweepy.OAuth1UserHandler(os.getenv('TWITTER_CONSUMER_KEY'), os.getenv('TWITTER_CONSUMER_SECRET_KEY'),
                                    os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
    api = tweepy.API(auth)
    actual_description = api.update_profile().description

    if re.search(r'listening to.*', actual_description):
        new_description = re.sub(r'listening to.*', 'listening to '+actual_track, actual_description)
    else:
        new_description = actual_description.strip() + '\nlistening to ' + actual_track

    api.update_profile(description=new_description)

    time.sleep(60)