import praw
user_agent = "ironist v0 by /u/byron https://github.com/bwallace/computational-irony"

import BeautifulSoup as bs
import urllib2

def setup():
    global r
    r = praw.Reddit(user_agent=user_agent)

def sample_comments_from_subreddit(subreddit, num_posts=10):
    subreddit = r.get_subreddit(subreddit)
    subreddit_posts = subreddit.get_hot(limit=num_posts)

def comments_for_thread(thread):
    comments = thread.comments
    for comment in comments:
        pass

def get_page(url, thread_id, out_dir="content"):
    page = urllib2.urlopen(url).read()
    # first dump just the page (HTML)
    with open(os.path.join(out_dir, thread_id + ".html")) as f_out:
        # note that the thread_id can be mapped back to a URL.
        f_out.write(page.text_context())

    # now parse and dump plaintext (title + body)


    # we'll use beautiful soup to parse this
    soup = bs(page.text_context())

    # find the title and body; ignore everything else


