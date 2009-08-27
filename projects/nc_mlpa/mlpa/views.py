from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti

from lingcod.manipulators.manipulators import * 
from manipulators import *
from django.contrib.gis.geos import *

from django.conf import settings
#from cjson import encode as json_encode
from django.utils import simplejson

import models

    
def mpaKmlAllGeom(request, id):
    """Handler for AJAX mpaKmlAllGeom request
    """
    mpa = get_object_or_404( models.MlpaMpa, pk=id )
    
    return HttpResponse( KmlWrap( mpa.kmlFolder(request.get_host()) ), content_type='text/plain') 
    
    
def mpaKml(request, id):
    """Handler for AJAX mpaKml request
    """
    mpa = get_object_or_404( models.MlpaMpa, pk=id )
    
    return HttpResponse( KmlWrap( '<Document><name>MPA</name>' + mpa.kmlFinalGeom(request.get_host()) + '</Document>' ), content_type='text/plain')
   
    
def mpaManipulatorList(request):
    """Handler for AJAX mpa manipulators request
    """
    manipulators = models.MlpaMpa.Options.manipulators
    manip_text = [(manipulator.Options.name) for manipulator in manipulators]
    
    return HttpResponse( simplejson.dumps( manip_text ))
    

