from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from django.conf import settings
from django.template import RequestContext

def map(request):
    """Main application window
    """
    return render_to_response('common/application.html', {
        'api_key': getattr(settings, "GOOGLE_MAPS_API_KEY", "API_KEY_NOT_SET")
    }, context_instance=RequestContext(request))