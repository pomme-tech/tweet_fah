import urllib.request
import json
import os
from datetime import datetime, timedelta, timezone

import yaml
import tweepy

def tweet_fah_status(event, callback):

    try:
        # local
        with open('./env.yaml') as f:
            os.environ.update(yaml.load(f))
    except FileNotFoundError as e:
        # Google Cloud Functions
        pass

    # URI of Folding@home API
    FH_API = os.getenv('fh_api')
    DONORNAME = os.getenv('donorname')
    uri = FH_API + DONORNAME

    # twitter api key
    # Cloud Functions の環境変数に定義する。
    CONSUMER_KEY = os.getenv('consumer_key')
    CONSUMER_SECRET = os.getenv('consumer_secret')
    ACCESS_TOKEN = os.getenv('access_token')
    ACCESS_TOKEN_SECRET = os.getenv('access_token_secret')

    # call Folding@home API
    ds_status = FoldingAtHome(uri).get_score()

    # make tweet body
    tweet_body = MakeTweetBody(DONORNAME, ds_status).make_tweet_body()

    # setting tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    # post to twitter
    api.update_status(tweet_body)

class FoldingAtHome:
    def __init__(self, site):
        self.site = site
    
    def get_score(self):
        r = urllib.request.urlopen(self.site)
        json_p = json.load(r)

        return [json_p["rank"], json_p["users"], json_p["score"], json_p["wus"], json_p["last"]]

class MakeTweetBody:
    def __init__(self, DONORNAME, ds_status):
        self.ds_donorname = DONORNAME
        self.ds_rank = ds_status[0]
        self.ds_tusers = ds_status[1]
        self.ds_credit = ds_status[2]
        self.ds_wus = ds_status[3]
        self.ds_last = ds_status[4]

    def make_tweet_body(self):
        JST = timezone(timedelta(hours=+9), 'JST')
        dt_now = datetime.now(JST)

        tweet_body = "Folding@home Donor Statistics\n"
        tweet_body += "\n"
        tweet_body += "<" + self.ds_donorname + ">\n"
        tweet_body += "Rank   : " + str(self.ds_rank) + " / " + str(self.ds_tusers) + "\n"
        tweet_body += "Credit : " + str(self.ds_credit) + "\n"
        tweet_body += "WUs    : " + str(self.ds_wus) + "\n"
        tweet_body += "update " + self.ds_last + "(UTC)\n"
        tweet_body += "\n"
        tweet_body += dt_now.strftime('%Y年%m月%d日 %H:%M:%S') + " 時点\n"
        tweet_body += "#foldingathome"

        return tweet_body
