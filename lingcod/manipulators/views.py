from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from django.template.loader import render_to_string

from lingcod.manipulators.manipulators import *
from django.db import models

from django.contrib.gis.geos import *
from lingcod.studyregion.models import StudyRegion
from lingcod.common.utils import KmlWrap
from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson

#from cjson import encode as json_encode
 
def mpaManipulatorList(request, app_name, model_name):
    """Handler for AJAX mpa manipulators request
    """
    try:
        model = ContentType.objects.get(app_label=app_name, model=model_name)
        manipulators = model.model_class().Options.manipulators        
    except Exception, e:
        return HttpResponse( "The following error was reported: '" + e.message + "', while generating manipulator list from application: " + app_name + " and model: " + model_name, status=404 )
    
    manip_text = [(manipulator.Options.name) for manipulator in manipulators]   
    
    return HttpResponse( simplejson.dumps( manip_text )) 
     
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
    
    html_response = ''

    # run the manipulators in the order presented
    for manipulator in manipulator_list:
        # try to bind the incoming manipulator string to an existing class
        manipClass = manipulatorsDict.get(manipulator)
        if not manipClass:
            return HttpResponse( "Manipulator " + manipulator + " does not exist.", status=404 )
        
        try:
            # 'GET' requests assume the intent is to get a related parameter-entry form
            if request.method == 'GET':
                if manipClass.Form.available:
                    form = manipClass.Form()
                    return render_to_response( 'common/base_form.html', RequestContext(request,{'form': form}))
                else: # this manipulator has no form, just error out
                    return HttpResponse( "Manipulator " + manipulator + " does not support GET requests.", status=501 )
                    
            else: # 'POST' request: run this manipulator
                if manipClass.Form.available: # validate a related form, if such exists
                    form = manipClass.Form( kwargs )
                    if form.is_valid():
                        initial_result = form.manipulation
                    else: # invalid parameters - bounce form back to user
                        return HttpResponse(simplejson.dumps({"message": "form is not valid (missing arguments?)", "html": render_to_string( 'common/base_form.html', {'form': form}, RequestContext(request)), "clipped_shape": None, "original_shape": None}))
                else: # no form exists - run this manipulator directly, passing the POST params directly as kwargs
                    manip_inst = manipClass( **kwargs )
                    initial_result = manip_inst.manipulate()
                    
                result = ensure_keys(initial_result)
                new_shape = result['clipped_shape'] 
                original_shape = result['original_shape']
                  
                # put the resulting shape back into the kwargs as the target_shape
                kwargs['target_shape'] = new_shape.wkt
                html_response = html_response + '<br/>' + result["html"] 
                
        except manipClass.InvalidGeometryException, e:
            return respond_with_error('3', e.message, None, None)
        except manipClass.InternalException, e:
            return respond_with_error('9', e.message, None, None)
        except manipClass.HaltManipulations, e:
            return respond_with_template(e.html, e.message, None, None, e.success)
        except Exception, e:
            return respond_with_error('11', e.message, None, None)      
    #end manipulator for loop      
                                           
    # manipulators ran fine and the resulting shape is ready for outbound processing
    new_shape.transform(settings.GEOMETRY_DB_SRID)
    #we should probably move this static value 20 to a settings variable
    new_shape = new_shape.simplify(20, preserve_topology=True)
    new_shape.transform(settings.GEOMETRY_CLIENT_SRID)
    
    return respond_with_template(html_response, result["message"], kmlDocWrap(new_shape.kml), kmlDocWrap(result["original_shape"].kml), result["success"])
    #return HttpResponse( simplejson.dumps({"clipped_shape": kmlDocWrap(new_shape.kml), "original_shape": kmlDocWrap(result["original_shape"].kml), "html": html_response, "message": result["message"], "success": result["success"]}))

def respond_with_template(status_html, message, clipped, original, success="1"):
    #status_html = status_html + render_to_string("manipulators/try_again_button.html", {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': message})
    return HttpResponse(simplejson.dumps({"clipped_shape": clipped, "original_shape": original, "html": status_html, "success": success}))
    
def respond_with_error(key, message, clipped, original, success="0"):
    status_html = render_to_string(BaseManipulator.Options.html_templates[key], {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': message})
    #status_html = status_html + render_to_string("manipulators/try_again_button.html", {'MEDIA_URL':settings.MEDIA_URL})
    return HttpResponse(simplejson.dumps({"clipped_shape": clipped, "original_shape": original, "html": status_html, "success": success}))
    
def ensure_keys(values):
    values.setdefault("message", "no message given")
    values.setdefault("html", "")
    values.setdefault("clipped_shape", None)
    values.setdefault("original_shape", None)
    values.setdefault("success", "1")
    return values
 
    
def kmlDocWrap( string ):
    return '<Document><Placemark> <Style> <LineStyle><color>ffffffff</color><width>2</width></LineStyle> <PolyStyle><color>8000ff00</color></PolyStyle> </Style>'+string+'</Placemark></Document>'

    
def testView( request ):
    trans_geom = StudyRegion.objects.current().geometry 
        
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
    