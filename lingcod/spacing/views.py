from django.template import RequestContext, loader, Context , Template
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template.loader import get_template
from lingcod.spacing.models import *

def Index(request):
    return render_to_response('map.html', RequestContext(request))

def LandKML(request):
    land = Land.objects.all()
    response = HttpResponse(land[0].kml(), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'land'
    return response