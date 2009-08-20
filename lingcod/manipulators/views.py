from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

from lingcod.manipulators.manipulators import *

from django.contrib.gis.geos import *
from lingcod.studyregion.models import StudyRegion
from lingcod.common.utils import KmlWrap
from django.conf import settings

from django.utils import simplejson

#from cjson import encode as json_encode


def multi_generic_manipulator_view(request, manipulators):
    '''
        multi_generic_manipulator_view takes a request and a list of manipulators
        and runs the manipulators in the order provided
    '''
    # conversion jiggery-pokery to get the QueryDict into appropriate kwarg format
    kwargs = {}
    for key,val in request.POST.items():
        kwargs[str(key)] = str(val)
                
    # parse out which manipulators are requested
    manipulator_list = manipulators.split(',')

    # run the manipulators in order presented
    for manipulator in manipulator_list:

        # try to bind the incoming manipulator string to an existing class
        manipClass = manipulatorsDict.get(manipulator)
        if not manipClass:
            return HttpResponse( "Manipulator " + manipulator + " does not exist.", status=404 )

        # 'get' requests assume the intent is to get a related parameter-entry form
        if request.method == 'GET':
            if manipClass.Form.available:
                form = manipClass.Form()
                return render_to_response( 'common/base_form.html', RequestContext(request,{'form': form}))
            else: # this manipulator has no form, just error out
                return HttpResponse( "Manipulator " + manipulator + " does not support GET requests.", status=405 )
                
        else: # post request: run this manipulator
            if manipClass.Form.available: # validate a related form, if such exists
                form = manipClass.Form( kwargs )
                if form.is_valid():
                
                    result = form.manipulation
                    new_shape = result['clipped_shape']
                    original_shape = result['original_shape']
                    
                    if original_shape is None: # common case is when all necessary kwargs are not provided
                        return HttpResponse(str(simplejson.dumps({"status_code": result["status_code"], "message": result["message"], "clipped_shape": None, "original_shape": None})))
                    
                    if new_shape is None: # common case is when target_shape is invalid
                        #return HttpResponse( 'From ' + manipulator + ':  ' + result['message'] )
                        return HttpResponse(str(simplejson.dumps({"status_code": result["status_code"], "message": result["message"], "clipped_shape": None, "original_shape": result["original_shape"].kml})))
                    
                    # put the resulting shape back into the kwargs as the target_shape
                    kwargs['target_shape'] = new_shape.wkt
                     
                else: # invalid parameters - bounce form back to user
                    #missing kwargs, will we eventually reinstate the base_form.html type response???
                    return HttpResponse(str(simplejson.dumps({"status_code": '6', "message": "form is not valid (missing arguments?)", "clipped_shape": None, "original_shape": None})))
                    #return render_to_response( 'common/base_form.html', RequestContext(request,{'form': form}))
                    
            else: # no form exists - run this manipulator directly, passing the POST params directly as kwargs

                manip_inst = manipClass( **kwargs )
                result = manip_inst.manipulate()
                new_shape = result["clipped_shape"] 
                original_shape = result['original_shape']

                if original_shape is None: # common case is when all necessary kwargs are not provided
                    return HttpResponse(str(simplejson.dumps({"status_code": result["status_code"], "message": result["message"], "clipped_shape": None, "original_shape": None})))
                
                if new_shape is None: # common case is when target_shape is invalid
                    #return HttpResponse( 'From ' + manipulator + ':  ' + result['message'] )
                    return HttpResponse(str(simplejson.dumps({"status_code": result["status_code"], "message": result["message"], "clipped_shape": None, "original_shape": result["original_shape"].kml})))
                    
                # put the resulting shape back into the kwargs as the target_shape
                kwargs['target_shape'] = new_shape.wkt
    #end manipulator for loop              
                
    # manipulators ran fine and the resulting shape is ready for outbound processing
    new_shape.transform(settings.GEOMETRY_DB_SRID)
    new_shape = new_shape.simplify(20, preserve_topology=True)
    new_shape.transform(settings.GEOMETRY_CLIENT_SRID)
                        
    #return HttpResponse(result, content_type = 'text/plain')
    
    return HttpResponse(str(simplejson.dumps({"status_code": result["status_code"], "message": result["message"], "clipped_shape": result["clipped_shape"].kml, "original_shape": result["original_shape"].kml})))
    #result = '<Document><Placemark><Style><LineStyle> <color>ffffffff</color> <width>2</width></LineStyle><PolyStyle> <color>80ffffff</color> </PolyStyle></Style>'+new_shape.kml+'</Placemark></Document>'
    #return render_to_response( 'studyregion/studyregion.html', RequestContext(request,{'extra_kml': result, 'api_key':settings.GOOGLE_API_KEY}))
    
   
def testView( request ):
    trans_geom = StudyRegion.objects.all()[0].geometry 
        
    w = trans_geom.extent[0]
    s = trans_geom.extent[1]
    e = trans_geom.extent[2]
    n = trans_geom.extent[3]
    
    center_lat = trans_geom.centroid.y 
    center_lon = trans_geom.centroid.x
            
    target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))
    target_shape.set_srid(settings.GEOMETRY_DB_SRID)
    target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
    
    new_req = HttpRequest()
    new_req.method = 'POST'
    new_req.POST.update({'target_shape':target_shape.wkt, "n":"40", "s":"20", "e":"-117", "w":"-118"})
    response = multi_generic_manipulator_view( new_req, 'ClipToStudyRegion,ClipToGraticule' )
    #response = multi_generic_manipulator_view( new_req, 'ClipToStudyRegion' )
    return response
    
    
    