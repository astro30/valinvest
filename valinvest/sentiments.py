import praw
import textblob
from .config import *
from functools import reduce
from collections import defaultdict
import re

def get_wsb_moves():
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)

    wsb = reddit.subreddit("wallstreetbets")

    moves_query = "title:What Are Your Moves Tomorrow author:AutoModerator"

    submissions = wsb.search('title:What Are Your Moves Tomorrow author:AutoModerator', sort='new', limit=1, time_filter='month')

    store_dict = dict()
    for submission in submissions:
        store_dict[str(submission.title)] = []
        submission.comments.replace_more(limit=None)
        for comment in submission.comments:
            store_dict[str(submission.title)].append(comment.body)

    return store_dict


def count_tickers_occurence(store_dict):
    counter = defaultdict(int)
    regex_query = '(' + reduce(lambda s, x: s + '|' + x, NASDAQ_100_TICKERS) + ')'
    for key in store_dict.keys():
        submission = store_dict[key]
        for comment in submission:
            findings = re.findall(regex_query, comment)
            findings = set([x.trim.upper() for x in findings])
        
            for match in findings:
                counter[match] += 1

    return counter
