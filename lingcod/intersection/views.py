from django.shortcuts import render_to_response
from django.template import RequestContext
from intersection.models import *

def split_to_single_shapefiles(request, multishape_pk, field_name):
    if request.user.is_staff():
        MultiFeatureShapefile.objects.get(pk=multishape_pk).split_to_single_feature_shapefiles(field_name)