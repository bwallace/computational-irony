import pdb

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt

from irony.models import Comment, CommentSegment, Label

def index(request):
    return HttpResponse("Hello, ironic world.")

def _lines_to_breaks(segments):
    for segment in segments:
        segment.text = segment.text.replace("\n", "<br/>")
    return segments

#@permission_required()
def show_comment(request, comment_id):
    comment_ = Comment.objects.get(pk=comment_id)
    #segments = CommentSegment.objects.filter(comment=comment_).order_by('segment_index')
    #return render_to_response("annotate.html", {"comment":comment_, "segments":segments})
    return render_to_response("annotate.html", {"comment":comment_})

#def next_comment_segments()
def get_comment_segments(request, comment_id):
    comment_ = Comment.objects.get(pk=comment_id)
    segments = CommentSegment.objects.filter(comment=comment_).order_by('segment_index')
    return render_to_response("comment_fragment.html", {"segments":segments})

def annotate_segments(request):
    ironic_segment_ids = request.POST.getlist('ironic_segments[]')
    # we are storing these as s{segment_id}; so just remove the 
    # prepended s.
    pdb.set_trace()
    ironic_segment_ids = [
        int(s_id.split("sid")[1]) for s_id in ironic_segment_ids]
    # @TODO get and label these segments


    '''
    # probably do not want to do this here; instead,
    #   handle getting the next comment on the client side

    ### TMP TMP TMP
    comment_ = Comment.objects.get(pk=1)
    segments = CommentSegment.objects.filter(comment=comment_).order_by('segment_index')
    ## END TMP

    return render_to_response("comment_fragment.html", 
                                {"comment":comment_, "segments":segments})
    '''

def login(request):
    pass

