'''
Code for harvesting reddit comments and contextualizing info (i.e., the
thread in which comments appear, and author comment history). This code
(and the data it collects) is part of our project on irony dection:

ARO grant 528674 
"Sociolinguistically Informed Natural Lanuage Processing: Automating Irony Detection"

Useful links:
https://github.com/reddit/reddit/wiki/API
https://praw.readthedocs.org

Note that we rely on PRAW to be good citizens w.r.t. reddit's API
(e.g., by throttling our requests, etc)
'''

import time
import csv 
import os
import pdb
import re
import sys
import datetime

import praw
user_agent = "ironist v0.5 by /u/byron https://github.com/bwallace/computational-irony"

import BeautifulSoup as bs
import urllib2

import html2text 

r = None # the reddit client

def setup():
    global r
    reload(sys)
    sys.setdefaultencoding("utf8")
    r = praw.Reddit(user_agent=user_agent)

def sample_comments_from_subreddit(subreddit, num_comments=500):
    if r is None:
        setup()

    subreddit = r.get_subreddit(subreddit)

    # the 500 is arbitrary; we just need enough posts
    # to cover the requested number of comments.
    subreddit_posts = subreddit.get_hot(limit=500)
    comments_so_far = 0
    while comments_so_far < num_comments:

        try:
            post = subreddit_posts.next()
        except:
            break
        print "processing post {0} ...".format(post)
        success, comment_count = process_post(post)
        if success:
            print "ok! pulled {0} comments from post".format(comment_count)
        else:
            print "failed -- moving on..."
        comments_so_far += comment_count
        print "{0} out of {1} comments processed thus far".format(comments_so_far, num_comments)

def try_to_get_page(post_url, post_id):
    success = False
    if post_url.lower().endswith(".jpg") or post_url.endswith(".gif"):
        # dont even try for images
        print "{0} looks like an image -- not downloading".format(post_url)
        return False

    URLS_to_avoid = ["reddit.com"]
    if any([s in post_url for s in URLS_to_avoid]):
        # we don't parse reddit pages; mostly because
        # we don't want to go over parsing limits.
        return False

    num_attempts, max_attempts = 0, 3
    while not success and num_attempts < max_attempts:
        try:
            get_page(post_url, post_id)
            return True
        except:
            print "failed to get page {0}... sleeping again".format(post_url)
            num_attempts += 1
            _sleep(num_attempts*5)
    return False

def process_post(post, max_comments=25, max_replies_per_comment=5):
    '''
    Takes a praw Submission object (which is a post) and:
        1. Dumps the post contents to disk
        2. Grabs up to max_comments first- and second- level comments 
            and dumps these to files (as well as the user 
            histories of the posters)

    Returns a tuple (bool, int) where the boolean indicates
    a success (insofar as we were at least able to pull the comment
    and associated external content) and the integer indicates
    the number of comments we processed in this post.
    '''
    # this handles dumping the 'content' to disk
    success = try_to_get_page(post.url, post.id)
    if not success:
        # we'll only keep comments for whicih we can 
        # also grab the content
        return (False, 0)

    count = 0
    top_level_comments = post.comments 
    for comment in top_level_comments[:-1]:
        succeeded = process_comment(comment)
        parent_id = comment.id
        if succeeded:
            count += 1
            second_level_comments = comment.replies
            second_level_count = 0
            for reply_comment in second_level_comments[:-1]:
                succeeded_second_level = process_comment(reply_comment, 
                                                parent_comment_id=parent_id)
                if succeeded_second_level:
                    count += 1
                    second_level_count += 1
                    if count >= max_comments:
                        return (True, count)
                    elif second_level_count >= max_replies_per_comment:
                        # we only sample up to max_replies_per_comment
                        # per parent at the 'second' level (replies)
                        break
        else:
            print "failed to grab a comment; sleeping for a few"
            _sleep()
        # technically we could get here if the 
        # replies result in exactly max_comments-1
        # comments
        if count >= max_comments:
            return (True, count)
    
    return (True, count)

def process_comment(comment, out_path="data/comments.csv", parent_comment_id=""):
    ''' 
    This routine sort of orchestrates data output. 

    Specifically, for the given comment object, this method 
    will append

    subreddit, thread_id, thread_title, comment_id, user, comment, comment_url, parent_comment_id, #downvotes, #upvotes, date

    to the comments.txt file *and* invoke the method to 
    retrieve and dump the commenters previous comments
    '''
    author = comment.author
 
    comment_out_str = [
        comment.subreddit, comment.submission.id, comment.submission.title, 
        comment.id, author, comment.body, comment.permalink, 
        parent_comment_id, str(comment.downs), str(comment.ups), str(datetime.datetime.now())]

    print "retrieving past comments for user {0}...".format(author)

    # now (try to) dump this user's past comments  
    if author is not None:  
        try:
            get_past_user_comments_str(author)
            print "success!"
        except:
            print "failed to get comments for user {0}".format(author)
            _sleep()
            return False
    
    print "ok -- now dumping comment."
    # only write out comment if we were successful in getting previous comments
    with open(out_path, 'a') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(comment_out_str)

    return True

def get_past_user_comments_str(user, out_path="data/users.csv", n=100):
    comment_str = [] 
    user_comments = list(user.get_comments(limit=n))
    print "ok! retrieved {0} comments for {1}".format(len(user_comments), user)

    ### note that we *append* to the users file!
    with open(out_path, 'a') as f_out:
        writer = csv.writer(f_out)
        for comment in user_comments:
            ''' user, comment, subreddit, thread_id, thread_title, thread_url, #downvotes, #upvotes, date, permalink '''
            cur_line = [
                user, comment.body, comment.subreddit, 
                comment.submission.id, comment.submission.title, 
                comment.submission.url, str(comment.downs), str(comment.ups),
                str(datetime.datetime.now()), comment.permalink]
            writer.writerow(cur_line)

            # 9/12/13 -- we're not going to try and pull the
            #       the external content for *every* post
            #       this is too much.
            '''
            # try to get the page, too
            success = try_to_get_page(comment.submission.url, comment.submission.id)
    
            if not success:
                # this is OK -- maybe an image, or a page from a domain
                # we can't handle
                print "-- failed to write {0} out".format(comment.submission.url)
            '''

def get_page(url, thread_id, out_dir="content"):
    page = None

    try:
        page = urllib2.urlopen(url).read()
    except:
        pass

    if page is None:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8'}

        # if this fails, we just pass the exception forward.
        req = urllib2.Request(url, headers=hdr)
        page = urllib2.urlopen(req).read()

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



if __name__ == "__main__":
    subreddit = sys.argv[1]
    sample_comments_from_subreddit(subreddit)