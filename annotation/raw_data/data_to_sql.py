'''
raw data -> sqlite
'''
import pdb
import csv
import sqlite3
import re

comments_path = "comments.csv"
users_path = "users.csv"
contents_dir = "contents"

db_path = "/Users/bwallace/dev/computational-irony/annotation/annotatr/ironate.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

split_expression = "(\.|!|\?)"

def csv_to_sql():
    with open(comments_path) as comments_f:
        comment_reader = csv.reader(comments_f)
        for comment in comment_reader:
            print comment
            _insert_comment(comment)

    with open(users_path) as users_f:
        user_reader = csv.reader(users_f)
        for user_comment in user_reader:
            _insert_past_user_comment(user_comment)
    

'''
    redditor = models.CharField(max_length=100)
    comment_text = models.CharField(max_length=10000)
    subreddit = models.CharField(max_length=200)
    thread_title = models.CharField(max_length=200)
    thread_id = models.CharField(max_length=50) # again, from reddit
    thread_url = models.CharField(max_length=500)
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    date = models.DateField() # date we *scraped* it, not the date it was posted!
    permalink = models.CharField(max_length=500)
'''
def _insert_past_user_comment(user_comment):
    '''
    user, comment, subreddit, thread_id, thread_title, thread_url, #downvotes, #upvotes, permalink
    '''
    #### @TODO
    # need to grab date here, too.
    user, comment, subreddit, thread_id, thread_title, \
        thread_url, n_downvotes, n_upvotes, permalink = [
                unicode(field, 'utf-8') for field in  user_comment]


    '''
    @TMP @TODO

    previously you were not dumping datetimes for fields, so we
    temporarily use an arbitrary date for dev reasons
    '''
    tmp_date = "2013-09-12 09:46:58.176198"
    cursor.execute(
        '''INSERT INTO irony_past_user_comment 
        (redditor, comment_text, subreddit, thread_id, thread_title, 
            thread_url, downvotes, upvotes, date, permalink)
        VALUES ((?), (?), (?), (?), (?), (?), (?), (?), (?), (?))
        ''', (user, comment, subreddit, thread_id, thread_title, 
              thread_url, n_downvotes, n_upvotes, tmp_date, permalink))
    conn.commit()

def _insert_comment(comment):
    subreddit, thread_id, thread_title, comment_id, user, \
      comment, comment_url, parent_comment_id, downvotes, upvotes, date = [
                unicode(field, 'utf-8') for field in  comment]
    
    cursor.execute(
      '''INSERT INTO irony_comment 
        (reddit_id, subreddit, thread_id, thread_title, redditor, parent_comment_id, 
         downvotes, upvotes, date, permalink)
        VALUES ((?), (?), (?), (?), (?), (?), (?), (?), (?), (?));
        ''', (comment_id, subreddit, thread_id, thread_title, user, parent_comment_id, 
              downvotes, upvotes, date, comment_url))

    conn.commit()
    _insert_comment_segments(cursor.lastrowid, comment)
    


def _insert_comment_segments(comment_id, comment_text):
    # just a very naive segmentation; assume that 
    # sentences will suffice

    segments = re.split(split_expression, comment_text)
    segment_i = 0
    for i in range(0, len(segments), 2):
        segment_text, delimiter = None, None
        if len(segments[i:i+2]) == 1:
            segment_text = segments[i]
            delimiter = ""
        else:
            segment_text, delimiter = segments[i:i+2]
        if segment_text.strip() != "":
            segment_text = segment_text + delimiter
            cursor.execute(
                '''INSERT INTO irony_comment_segment(comment_id, segment_index, text) VALUES ((?), (?), (?));
                ''', (comment_id, segment_i, segment_text))
            segment_i += 1
            conn.commit()

    
    #pdb.set_trace()
    #for segment_i, segment in enumerate(segments):
    #    cursor.execute(
    #        '''INSERT INTO ironate_comment_segment(comment_id, segment_index, text) VALUES ((?), (?), (?));
    #        ''', (comment_id, segment_i, segment))
    #conn.commit()

