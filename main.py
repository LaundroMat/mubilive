import os
import time
import requests
import tweepy
from dotenv.main import logger
from pydantic import BaseSettings

SECONDS_BETWEEN_CHECKS = 60


class Settings(BaseSettings):
    twitter_api_key: str
    twitter_api_secret: str
    twitter_bearer_token: str

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


def check(current_movie_id: int = None):
    current_movie_id = int(current_movie_id) if current_movie_id else None

    r = requests.get('https://mubi.com/live.json')
    data = r.json()
    film_info = data['film_programming']

    if film_info['id'] != current_movie_id:
        tweet_body = f'''
mubi.com/live now showing {film_info['title']} ({film_info['directors']}, {film_info['country']}, {film_info['year']}).

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
        while len(".".join(parts)) > 278:
            parts.pop()

        status = ".".join(parts) + "."
        api.update_with_media(filename, status=status)
        os.remove(filename)
    else:
        print("No new movie (yet).")

    time.sleep(SECONDS_BETWEEN_CHECKS)
    check(film_info['id'])


if __name__ == "__main__":
    check()
