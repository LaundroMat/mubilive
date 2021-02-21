import os
import time

import arrow
import requests
import tweepy
from loguru import logger
from pydantic import BaseSettings

SECONDS_BETWEEN_CHECKS = 60


class Settings(BaseSettings):
    twitter_api_key: str
    twitter_api_secret: str

    twitter_access_token: str
    twitter_access_token_secret: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()


def create_api():
    auth = tweepy.OAuthHandler(settings.twitter_api_key, settings.twitter_api_secret)
    auth.set_access_token(settings.twitter_access_token, settings.twitter_access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


api = create_api()

current_movies = [
    {
        'country': 'Ireland',
        'flag': '🇮🇪',
        'url': 'https://swksavcqn2.execute-api.eu-west-1.amazonaws.com/MubiLive',
        'current_movie_id': 0,
    }, {
        'country': 'France',
        'flag': '🇫🇷',
        'url': 'https://pszitemmtj.execute-api.eu-west-3.amazonaws.com/MubiLive',
        'current_movie_id': 0
    }, {
        'country': 'US',
        'flag': '🇺🇸',
        'url': 'https://m4x6b73f0j.execute-api.us-east-1.amazonaws.com/default/MubiLIve',
        'current_movie_id': 0
    },
    {
        'country': 'Germany',
        'flag': '🇩🇪',
        'url': 'https://226nqjv99d.execute-api.eu-central-1.amazonaws.com/default/MubiLive',
        'current_movie_id': 0
    },

]


def check(current_movies: list):
    for movie in current_movies:
        r = requests.get(movie['url'])
        data = r.json()
        logger.debug(data)
        film_info = data['film_programming']

        if film_info['id'] != movie['current_movie_id']:
            logger.debug(f"New movie: {film_info['title']}")
            movie['current_movie_id'] = film_info['id']
            tweet_body = f'''
{film_info['title']} ({film_info['directors']}, '''
            if film_info.get('country'):
                tweet_body += f"{film_info.get('country')}"
            tweet_body += f'''
{film_info['year']}) just started on mubi.com/live in {movie['flag']} {movie['country']}.
    
{film_info['excerpt']}
'''
            tweet_img = film_info['stills']['retina']

            filename = f"{film_info['title']}.jpg"
            r = requests.get(tweet_img)
            if r.status_code == 200:
                with open(filename, 'wb') as image:
                    for chunk in r:
                        image.write(chunk)

            parts = tweet_body.split(".")
            while len(".".join(parts)) > 255:
                parts.pop()

            status = ".".join(parts) + "."
            api.update_with_media(filename, status=status)
            os.remove(filename)
        else:
            print(f"No new movie for {movie['country']} (yet). Still watching {film_info['title']}.")

    time.sleep(SECONDS_BETWEEN_CHECKS)
    check(current_movies)


if __name__ == "__main__":
    check(current_movies)
