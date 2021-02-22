import os
import time

import arrow
import requests
import tweepy
from loguru import logger
from pydantic import BaseSettings

from conf import settings
from db import db_client, q

SECONDS_BETWEEN_CHECKS = 60


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
    return api


api = create_api()



def check():
    query = db_client.query(q.map_(lambda doc: q.get(doc), q.paginate(q.documents(q.collection('nowShowing')))))

    for doc in query['data']:
        country = doc['data']

        r = requests.get(country['feed'])
        mubi_data = r.json()
        mubi_film_info = mubi_data['film_programming']

        if mubi_film_info['id'] != country['currentMovieId']:
            logger.debug(f"New movie for {country['name']}: {mubi_film_info['title']}")

            db_client.query(q.update(doc['ref'], {"data": {"currentMovieId": mubi_film_info['id']}}))

            tweet_body = f'''{mubi_film_info['title']} ({mubi_film_info['directors']}, '''
            if mubi_film_info.get('country'):
                tweet_body += f"{mubi_film_info.get('country')} "
            tweet_body += f'''{mubi_film_info['year']}) just started on mubi.com/live in {country['flag']} {country['name']}.
    
{mubi_film_info['excerpt']}
'''
            tweet_img = mubi_film_info['stills']['retina']

            filename = f"{mubi_film_info['title']}.jpg"
            r = requests.get(tweet_img)
            if r.status_code == 200:
                with open(filename, 'wb') as image:
                    for chunk in r:
                        image.write(chunk)

            parts = tweet_body.split(".")
            while len(".".join(parts)) > 255:
                parts.pop()

            status = ".".join(parts) + "."

            if not settings.test:
                api.update_with_media(filename, status=status)
            else:
                logger.debug(status, filename)
            os.remove(filename)
        else:
            logger.debug(f"No new movie for {country['name']} (yet). Still watching {mubi_film_info['title']}.")

    time.sleep(SECONDS_BETWEEN_CHECKS)
    check()


if __name__ == "__main__":
    check()
