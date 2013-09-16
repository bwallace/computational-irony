from django.db import models
from django.contrib.auth.models import User

'''
:id: arbitrary identifying number.
:reddit_id: unique identifying string from reddit
:subreddit: string capturing the subreddit to which this comment belongs
:thread: identifies the thread (i.e., post); again a unique string from reddit
:redditor: unique string ID identifying the commentor (author)
:parent_comment_id: this will be NULL for all top-level comments. for comments that are replies, this will be a comment identifier.
:upvotes: number of upvotes this comment received
:downvotes: number of downvotes
:date: date this comment was scraped (*not* when posted)
:permalink: url to comment
'''
class comment(models.Model):
    # identifier from reddit
    reddit_id = models.CharField(max_length=50)
    subreddit = models.CharField(max_length=200)
    thread_title = models.CharField(max_length=200)
    thread_id = models.CharField(max_length=50) # again, from reddit
    redditor = models.CharField(max_length=100)
    parent_comment_id = models.CharField(max_length=50, null=True)
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    date = models.DateField()
    permalink = models.CharField(max_length=500)

'''
A comment segment is part of segment (comments comprise disjoint
segments).

:id: unique segment idenfier (number; *not* from reddit)
:comment_ID: the ID of the comment of which this segment is a part
:segment_index: the relative location of this segment within the larger comment. 
    This is numerical, so ordering segments by this field for a given <comment_ID> 
    produces the original comment.
:text: finally, the actual body of the segment (string).
'''
class comment_segment(models.Model):
    comment = models.ForeignKey(comment)
    segment_index = models.IntegerField()
    text = models.CharField(max_length=10000) # may be long...

'''
:id: unique identifier for this label (*not* from reddit)
:segment_id: the segment this label refers to.
:labeler: the person (user) who provided this label.
:label: y \in {-1,0,1} for unironic, "i don't know" and ironic, respectively.
:used_context: boolean indicating whether 'context' was used to make this judgement.
:confidence: score on a Likert scale expressing subjective confidence in the assigned label.
'''
class label(models.Model):
    segment = models.ForeignKey(comment_segment)
    labeler = models.ForeignKey(User)
    label = models.IntegerField() # -1, 0, 1
    used_context = models.BooleanField(default=False)
    confidence = models.PositiveIntegerField() # 1,2,3


'''
these are comments used for context; we do not seek labels
for these.

:redditor: i.e., the comment author; reddit identifier (string)
:comment: the text of the comment (string)
:subreddit: the subreddit to which this comment belongs
:thread_id: reddit identifier for thread to which this comment belongs
:thread_title: title of the owning thread
:thread_url: permalink to the thread
:downvotes: number of downvotes this comment had received at time of scraping
:upvotes: ditto, upvotes
:permalink: permalink to the comment
'''
class past_user_comment(models.Model):
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
