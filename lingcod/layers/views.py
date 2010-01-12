from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from models import *
from lingcod.common import mimetypes
from django.conf import settings
import os


def get_public_layers(request):
    """Returns uploaded kml from the :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` object marked ``active``.
    """
    layer = get_object_or_404(PublicLayerList, active=True)
    return HttpResponse(layer.kml.read(), mimetype=mimetypes.KML)
    
def get_ecotrust_layers(request):
    """Returns uploaded kml from the :class:`EcotrustLayerList <lingcod.layers.models.EcotrustLayerList>` object marked ``active``.
    """
    layer = get_object_or_404(EcotrustLayerList, active=True)
    return HttpResponse(layer.kml.read(), mimetype=mimetypes.KML)
    
def get_map(request, group_name, layer_name, z=None, x=None, y=None, ext=None, root=settings.GIS_DATA_ROOT):
    #old root was 'U:/dev/ecotrust_data_layers/maps/'
    root_path = os.path.join(root, 'pvg', group_name, layer_name)
    if z is None:
        doc_file = os.path.join(root_path, 'doc.kml')
        doc_kml = open(doc_file).read()
        return HttpResponse(doc_kml, mimetype=mimetypes.KML)  
    elif ext == 'kml':
        kml_file = os.path.join(root_path, z, x, y+'.kml')
        tile_kml = open(kml_file).read()
        return HttpResponse(tile_kml, mimetype=mimetypes.KML)
    else:
        png_file = os.path.join(root_path, z, x, y+'.png')
        tile_png = open(png_file, "rb").read()
        return HttpResponse(tile_png, mimetype='image/png')
   
def get_contour(request, group_name, layer_name, z=None, x=None, y=None, ext=None, root=settings.GIS_DATA_ROOT):
    root_path = os.path.join(root, 'pvc', group_name, layer_name)
    if z is None:
        doc_file = os.path.join(root_path, 'doc.kml')
        doc_kml = open(doc_file).read()
        return HttpResponse(doc_kml, mimetype=mimetypes.KML)
    z = int(z)
    x = int(x)
    y = int(y)
    dims = (  "%02d" % z,
                "%03d" % int(x / 1000000),
                "%03d" % (int(x / 1000) % 1000),
                "%03d" % (int(x) % 1000),
                "%03d" % int(y / 1000000),
                "%03d" % (int(y / 1000) % 1000),
                "%03d.%s" % (int(y) % 1000, ext)
            )
            
    file_path = os.path.join(root_path, dims[0], dims[1], dims[2], dims[3], dims[4], dims[5], dims[6]) 
    if ext == 'kml':
        tile = open(file_path).read()
        return HttpResponse(tile, mimetype=mimetypes.KML)
    else:
        tile = open(file_path, "rb").read()
        return HttpResponse(tile, mimetype='image/png')

    
 