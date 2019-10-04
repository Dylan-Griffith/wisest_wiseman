import praw
import config
import schedule
import time
from random import choice
import os
import pandas as pd

comment_id_file = 'comments_replied_to.txt'
submission_id_file = 'submission_replied_to.txt'


def authenticate():
    print('Authenticating User....')
    reddit = praw.Reddit(client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent=config.user_agent,
                         username=config.username,
                         password=config.password)
    print("User '{user}' Authenticated".format(user=reddit.user.me()))
    return reddit


def get_replied_ids(file):
    if not os.path.isfile(file):
        replied_ids = []
    else:
        with open(file, 'r') as fin:
            replied_ids = fin.read()
            replied_ids = replied_ids.split('\n')
            replied_ids = list(filter(None, replied_ids))

    return replied_ids


def clean_comments():
    for comment in me.comments.hot():
        if comment.score < 1:
            print(comment.body)
            print('Comment deleted!')
            comment.delete()


parables_df = pd.read_csv('parables.csv', header=None)
parables = list(parables_df['text'])

orig_par = parables

SUBREDDITS = ["Showerthoughts", 'Iamverysmart', 'memes', 'dankmemes', 'funny',
              'videos', 'wholesomememes', 'WatchPeopleDieInside', 'mildlyinteresting']

banned_subreddits = ['politicalhumor', 'pewdiepiesubmissions', 'relationship_advice',
                     'todayilearned', 'Philosophy', 'Politics', 'unpopularopinion']

reddit = authenticate()
me = reddit.user.me()


def main():
    global parables
    SUBREDDIT = choice(SUBREDDITS)
    print(SUBREDDIT)
    submission_id_list = get_replied_ids(submission_id_file)

    # resets parables list if empty
    if not parables:
        print('adding more....')
        parables = list(parables_df['text'])

    # Finds top  hot post from subreddit and comments to one of the top level comments
    for submission in reddit.subreddit(SUBREDDIT).hot(limit=10):
        if not submission.stickied and submission not in submission_id_list and submission.score > 1000:
            print('TITLE: ', submission.title)
            top_comments = submission.comments.list()[:4]
            for comment in top_comments:
                if comment.author == 'AutoModerator' or comment.score < 50:
                    top_comments.remove(comment)
            random_comment = choice(top_comments)

            with open('submission_replied_to.txt', 'a') as fout:
                fout.write(submission.id + '\n')

            random_parable = choice(parables)
            parables.remove(random_parable)

            print(random_comment.body)
            print(random_parable)
            random_comment.reply(random_parable)

            break


if __name__ == '__main__':
    schedule.every(15).minutes.do(main)
    schedule.every().hour.do(clean_comments)

    while True:
        schedule.run_pending()
        time.sleep(1)

