import pdb
import random

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from irony.models import Comment, CommentSegment, Label, User

def index(request):
    return HttpResponse("Hello, ironic world.")

def _lines_to_breaks(segments):
    for segment in segments:
        segment.text = segment.text.replace("\n", "<br/>")
    return segments

def _get_comment_segments(comment_):
    return CommentSegment.objects.filter(comment=comment_).order_by('segment_index')


'''
# @antiquated
def show_comment(request, comment_id):
    comment_ = Comment.objects.get(pk=comment_id)
    return render_to_response("annotate.html", {"comment":comment_})
'''

def _get_next_comment_for_user(user):
    already_labeled_comments = Label.objects.filter(labeler=user)
    unlabeled_comments = Comment.objects.exclude(
        id__in=[comment.id for comment in already_labeled_comments])
    if len(unlabeled_comments) == 0:
        return HttpResponse("relax, you've labeled everything.")

    random_index = random.randint(0,len(unlabeled_comments)-1)
    return unlabeled_comments[random_index]

def get_next_comment_fragment(request):
    user = request.user
    selected_comment = _get_next_comment_for_user(user)
    return get_comment_segments(request, selected_comment.id)

def get_comment_segments(request, comment_id):
    comment_ = Comment.objects.get(pk=comment_id)
    segments = _get_comment_segments(comment_)
    return render_to_response("comment_fragment.html", 
            {"segments":segments, "comment":comment_, 
                "comment_id":comment_.id})

def get_next_comment(request):
    user = request.user
    next_comment = _get_next_comment_for_user(user)
    return render_to_response("annotate.html", {"comment":next_comment})

def annotate_segments(request):
    ironic_segment_ids = request.POST.getlist('ironic_segments[]')
    # we are storing these as s{segment_id}; so just remove the 
    # prepended s.
    ironic_segment_ids = [
        int(s_id.split("sid")[1]) for s_id in ironic_segment_ids]
   
    # was this decision forced?
    forced_decision  = request.POST.get("forced_decision")

    # get labeler confidence
    confidence = request.POST.get("confidence")
    conf_int = {
        "conf_low":0,
        "conf_med":1,
        "conf_high":2
    }[confidence]

    comment_id = request.POST.get("comment_id")
    # get all segments from the associated comment; the assumption
    # is that any *not* labeled as ironic were labeled as sincere.
    comment = Comment.objects.get(pk=comment_id)
    all_comment_segments = _get_comment_segments(comment)
    for segment in all_comment_segments:
        segment_lbl = -1
        if segment.id in ironic_segment_ids:
            segment_lbl = 1

        lbl_obj = Label.objects.create(
            labeler=request.user, segment=segment, label=segment_lbl, 
            viewed_thread=False, viewed_page=False, confidence=conf_int, 
            comment=comment, forced_decision=forced_decision)
        lbl_obj.save()

    # I'm actually not really sure if this is the correct thing
    # to do here, but it seems reasonable?
    messages.success(request, "success message")
    return HttpResponse(messages)
    


def login(request):
    pass

