from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
# from lingcod.simplefaq.models import *


def sitemap(request):
    return render_to_response('sitemap.xml') 

