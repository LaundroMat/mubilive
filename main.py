import time
import requests
from loguru import logger

SECONDS_BETWEEN_CHECKS = 60


def check(current_movie_id: int):
    current_movie_id = int(current_movie_id)

    r = requests.get('https://mubi.com/live.json')
    data = r.json()
    film_info = data['film_programming']

    if film_info['id'] != current_movie_id:
        tweet_body = f'''
Mubi Live is now showing {film_info['title']} ({film_info['directors']}, {film_info['country']} {film_info['year']})

{film_info['excerpt']}
'''
        tweet_img = film_info['stills']['retina']

        # tweet this
        logger.debug(tweet_body, tweet_img)
    else:
        logger.debug("No new movie (yet).")
        time.sleep(SECONDS_BETWEEN_CHECKS)

    check(film_info['id'])
