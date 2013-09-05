import praw
user_agent = "ironist v0 by /u/byron https://github.com/bwallace/computational-irony"

import BeautifulSoup as bs
import urllib2

import html2text 

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

def _clean_up(some_html):
    _none_to_empty = lambda s : s if s is not None else ""
    some_html = _none_to_empty(some_html)
    return html2text.html2text(some_html)


def _remove_js(soup):
    for script in soup("script"):
        script.extract()
    return soup

def get_page(url, thread_id, out_dir="content"):
    page = urllib2.urlopen(url).read()
    # first dump just the page (HTML)
    with open(os.path.join(out_dir, thread_id + ".html")) as f_out:
        # note that the thread_id can be mapped back to a URL.
        f_out.write(page.text_context())

    # now parse and dump plaintext (title + body)
    # we'll use beautiful soup to parse this
    soup = bs(page.text_context())
    # remove js
    title, body = "", ""
    if soup is not None:
        soup = _remove_js(soup)
        # find the title and body; ignore everything else
        title = _clean_up(soup.head.title.text)
        body = _clean_up(soup.head.body.text)

    with open(os.path.join(out_dir, thread_id + ".txt")) as f_out:
        f_out.write("{0}\n\n{1}".format(title, body))



