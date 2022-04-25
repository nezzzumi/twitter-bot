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

auth = tweepy.OAuth1UserHandler(os.getenv('TWITTER_CONSUMER_KEY'), os.getenv('TWITTER_CONSUMER_SECRET_KEY'),
                                os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

last_track = ''

while True:
    try:
        actual_track = get_current_song(os.getenv('LASTFM_USER'), os.getenv('LASTFM_API_KEY'))
    except Exception as e:
        print('Erro ao buscar música atual: ', e)
        continue
    
    if actual_track == last_track:
        continue

    last_track = actual_track

    actual_description = api.update_profile().description

    if not actual_track:
        if not re.search(r'listening to.*', actual_description):
            continue

        new_description = re.sub(r'listening to.*', '', actual_description)
    else:
        print(
            f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] listening to: '+actual_track)

        if re.search(r'listening to.*', actual_description):
            new_description = re.sub(
                r'listening to.*', 'listening to '+actual_track, actual_description)
        else:
            new_description = actual_description.strip() + '\n\nlistening to ' + actual_track
    try:
        api.update_profile(description=new_description)
    except Exception as e:
        print('Erro ao atualizar descrição: ', e)
        continue

    time.sleep(60)
