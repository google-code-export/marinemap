# Create your views here.
from django.http import HttpResponse
from lingcod.raster_stats.models import zonal_stats, RasterDataset, ZonalStatsCache
from django.core import serializers
from django.contrib.gis.geos import fromstr

def stats_for_geom(request,pk):
    # Confirm that we have a valid polygon geometry
    if 'geom_txt' in request.REQUEST: 
        geom_txt = str(request.REQUEST['geom_txt'])
    else:
        return HttpResponse("Must supply a geom_txt parameter", status=404)
    
    try:
        geom = fromstr(geom_txt)
    except:
        return HttpResponse("Must supply a parsable geom_txt parameter (wkt or json)", status=404)
 
    # Confirm raster with pk exists
    try:
        raster = RasterDataset.objects.get(pk=pk)
    except:
        return HttpResponse("No raster with pk of %s" % pk, status=404)

    #TODO check if continuous
    zonal = zonal_stats(geom, raster)
    zonal.save()
    zqs = ZonalStatsCache.objects.filter(pk=zonal.pk)
    data = serializers.serialize("json", zqs)

    return HttpResponse(data, mimetype='application/javascript')
