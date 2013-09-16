from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User

from irony.models import comment, comment_segment

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

#@permission_required()
def show_comment(request, comment_id):
    comment_ = comment.objects.get(pk=comment_id)
    print request.user.is_authenticated()
    return HttpResponse(str(comment_))

def login(request):
    pass