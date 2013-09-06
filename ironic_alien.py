'''
Code for harvesting reddit comments and contextualizing info (i.e., the
thread in which comments appear, and author comment history). This code
(and the data it collects) is part of our project on irony dection:

ARO grant 528674 
"Sociolinguistically Informed Natural Lanuage Processing: Automating Irony Detection"

Useful links:
https://github.com/reddit/reddit/wiki/API
https://praw.readthedocs.org

Note that we rely on PRAW to be good citizens w.r.t. reddit's API:

'''

import csv 
import os
import pdb
import re
import sys

import praw
user_agent = "ironist v0 by /u/byron https://github.com/bwallace/computational-irony"

import BeautifulSoup as bs
import urllib2

import html2text 

r = None # the reddit client

def setup():
    global r
    reload(sys)
    sys.setdefaultencoding("utf8")
    r = praw.Reddit(user_agent=user_agent)

def sample_comments_from_subreddit(subreddit, num_posts=10):
    if r is None:
        setup()

    subreddit = r.get_subreddit(subreddit)
    subreddit_posts = subreddit.get_hot(limit=num_posts)
    for post in subreddit_posts:
        print "processing post {0} ...".format(post)
        process_post(post)
        print "done."

def process_post(post, max_comments=20):
    '''
    Takes a praw Submission object (which is a post) and:
        1. Dumps the post contents to disk
        2. Grabs up to 100 first- and second- level comments 
            and dumps these to files (as well as the user 
            histories of the posters)
    '''
    # this handles dumping the 'content' to disk
    success = False
    while not success:
        try:
            success = True
            get_page(post.url, post.id)
        except:
            print "failed to get page {0}... sleeping again".format(post.url)
            success = False
            _sleep()

    count = 0
    top_level_comments = post.comments 
    for comment in top_level_comments[:-1]:
        process_comment(comment)
        count += 1
        second_level_comments = comment.replies
        for reply_comment in second_level_comments[:-1]:
            process_comment(reply_comment)
            count += 1
            if count >= max_comments:
                return False
        # technically we could get here if the 
        # replies result in exactly max_comments-1
        # comments
        if count >= max_comments:
            return False
    
    return True

def process_comment(comment, out_path="data/comments.csv"):
    ''' 
    This routine sort of orchestrates data output. 

    Specifically, for the given comment object, this method 
    will append

        thread_id, user, comment, url, subreddit 

    to the comments.txt file *and* invoke the method to 
    retrieve and dump the commenters previous comments
    '''
    author = comment.author

    comment_out_str = [
        comment.submission.id, author,
        comment.body, comment.permalink, comment.subreddit]

    with open(out_path, 'a') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(comment_out_str)

    print "retrieving past comments for user {0}...".format(author)

    # now dump this user's past comments    
    get_past_user_comments_str(author)



def get_past_user_comments_str(user, out_path="data/users.csv", n=50):
    comment_str = [] 
    user_comments = user.get_comments(limit=n)

    ### note that we *append* to the users file!
    with open(out_path, 'a') as f_out:
        writer = csv.writer(f_out)
        for comment in user_comments:
            ''' user, comment, url, subreddit '''
            cur_line = [
                user, comment.body, comment.subreddit, comment.permalink]
            writer.writerow(cur_line)


def get_page(url, thread_id, out_dir="content"):
    page = urllib2.urlopen(url).read()
    # first dump just the page (HTML)
    with open(os.path.join(out_dir, thread_id + ".html"), 'w') as f_out:
        # note that the thread_id can be mapped back to a URL.
        f_out.write(page)

    # now parse and dump plaintext (title + body)
    # we'll use beautiful soup to parse this
    soup = bs.BeautifulSoup(page)
    # remove js
    title, body = "", ""
    if soup is not None:
        soup = _remove_js(soup)
        # find the title and body; ignore everything else
        title = _clean_up(soup.head.title.text)
        #body = _clean_up(soup.body.text)
        body = _clean_up(get_visible_text(soup))
        #pdb.set_trace()

    with open(os.path.join(out_dir, thread_id + ".txt"), 'w') as f_out:
        f_out.write("{0}\n\n{1}".format(title, body))


''' helper methods '''

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def get_visible_text(soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(visible, texts)
    return " ".join(visible_texts)

def _clean_up(some_html):
    _none_to_empty = lambda s : s if s is not None else ""
    some_html = _none_to_empty(some_html)
    return html2text.html2text(some_html)


def _remove_js(soup):
    for script in soup("script"):
        script.extract()
    return soup

def _sleep(t=5):
    time_to_sleep = t
    print "zzzzzz for {0}...".format(t)
    time.sleep(t)
    print "i'm up!"

