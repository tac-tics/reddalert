from datetime import datetime
import time
from pprint import pformat
import logging
import praw
import sys
import getpass
import configparser
import os

from twilio.rest import Client

from prawcore.exceptions import ResponseException, RequestException, OAuthException
from twilio.base.exceptions import TwilioRestException

config = configparser.ConfigParser()

REDDIT_USER = os.environ['REDDIT_USER']
REDDIT_INI = os.environ.get('REDDIT_INIT', '/data/credentials/reddit/' + REDDIT_USER)
config.read(REDDIT_INI)
config.read('/data/credentials/twilio/twilio')

USER_AGENT = 'alittlebot'

seen_ids = []
logging.info('Starting...')

def connect_to_reddit():
    return praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=USER_AGENT,
            username=config['reddit']['username'],
            password=config['reddit']['password'],
        )

def connect_to_twilio():
    return Client(config['twilio']['secret'], config['twilio']['token'])

def has_new_messages(messages):
    for message in messages:
        if message.id not in seen_ids:
            return True
    return False

while True:
    try:
        reddit = connect_to_reddit()
        messages = list(reddit.inbox.unread())
        logging.info('Messages found: ', len(messages))
        del reddit

        if has_new_messages(messages):
            logging.info('Found {} messages'.format(len(messages)))
            twilio_client = connect_to_twilio()

            for message in messages:
                author = message.author.name
                body = message.body
                if message.id not in seen_ids:
                    seen_ids.append(message.id)
                    twilio_client.messages.create(
                            to=config['twilio']['callback'],
                            from_=config['twilio']['number'],
                            body='[{}->{}] {}'.format(author, REDDIT_USER, body[:50]))
                    body = '[{}->{}] {}'.format(author, REDDIT_USER, body[:50])
                    logging.info(body)

            del twilio_client

    except TwilioRestException as e:
        logging.info(str(e))

    except ResponseException as e:
        logging.info(str(e))

    except RequestException as e:
        logging.info(str(e))

    except OAuthException as e:
        logging.info(str(e))

    time.sleep(15)
