import pdb

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.views.generic import View
from django.views.generic.base import TemplateView

from irony.models import Comment, CommentSegment, Label

def index(request):
    return HttpResponse("Hello, ironic world.")

#@permission_required()
def show_comment(request, comment_id):
    comment_ = Comment.objects.get(pk=comment_id)
    
    segments = CommentSegment.objects.filter(comment=comment_).order_by('segment_index')
    return render_to_response("annotate.html", {"comment":comment_, "segments":segments})


def login(request):
    pass

