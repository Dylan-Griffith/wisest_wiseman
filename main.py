import praw
import config
import schedule
import time
from random import choice
import pickle
import os

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


with open('formatted_parables.pickle', 'rb') as fin:
    parables = pickle.load(fin)

orig_par = parables

SUBREDDITS = ["politics", 'teenagers', 'memes', 'relationship_advice', 'Showerthoughts']
reddit = authenticate()
me = reddit.user.me()


def main():
    global parables
    SUBREDDIT = choice(SUBREDDITS)
    print(SUBREDDIT)
    comment_id_list = get_replied_ids(comment_id_file)
    submission_id_list = get_replied_ids(submission_id_file)

    # Finds top  hot post from subreddit and comments to one of the top level comments
    for submission in reddit.subreddit(SUBREDDIT).hot(limit=10):
        if not submission.stickied and submission not in submission_id_list and submission.score > 1000:
            print('TITLE: ', submission.title)
            top_comments = submission.comments.list()[:4]
            for comment in top_comments:
                if comment.author == 'AutoModerator' or comment.score < 50:
                    top_comments.remove(comment)
            random_comment = choice(top_comments)

            with open('comments_replied_to.txt', 'a') as fout:
                fout.write(random_comment.id + '\n')

            with open('submission_replied_to.txt', 'a') as fout:
                fout.write(submission.id + '\n')

            # resets parables list if empty
            if not parables:
                parables = orig_par

            random_parable = choice(parables)
            parables.remove(random_parable)

            print(random_comment.body)
            print(random_parable)
            random_comment.reply(random_parable)

            with open('Comments.txt', 'a') as fout:
                fout.write(SUBREDDIT + '\n')
                fout.write('TITLE: ' + submission.title + '\n')
                fout.write('ID: ' + submission.id + '\n')
                fout.write('Comment: ' + random_comment.body + '\n')
                fout.write(random_parable + '\n')

            break


if __name__ == '__main__':
    schedule.every(15).minutes.do(main)
    schedule.every().hour.do(clean_comments)

    while True:
        schedule.run_pending()
        time.sleep(1)

