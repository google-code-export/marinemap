from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from lingcod.intersection.models import *
from lingcod.intersection.forms import *

def split_to_single_shapefiles(request, mfshp_pk):
    if request.user.is_staff:
        if request.method == 'POST':
            form = SplitToSingleFeaturesForm(mfshp_pk, request.POST)
            if form.is_valid():
                mfshp_pk = form.cleaned_data['mfshp_pk']
                shp_field = form.cleaned_data['shp_field']
                mfshp = MultiFeatureShapefile.objects.get(pk=mfshp_pk)
                mfshp.split_to_single_feature_shapefiles(str(shp_field))
                return HttpResponseRedirect('../../../singlefeatureshapefile')
        else:
            form = SplitToSingleFeaturesForm(mfshp_pk)
    else:
        return HttpResponseForbidden
    
    return render_to_response('split_to_single_feature_shapefiles.html', {'form': form, 'mfshp_pk_key': mfshp_pk})

def intersect(request):
    if request.method == 'POST':
        form = TestPolygonForm(request.POST)
        if form.is_valid():
            geom = geos.fromstr(form.cleaned_data['geometry'])
            geom.transform(3310)
            result = intersect_the_features(geom)
            return render_to_response('generic_results.html', {'result': result})
    else:
        form = TestPolygonForm()
#    result = intersect_the_features(geom)
#    return render_to_response('generic_results.html', {'result': result})
    return render_to_response('polygon_form.html', {'form': form})