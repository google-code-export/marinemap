from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.db import connection

def kml_doc_from_queryset(qs):
    dict = {}
    placemarks = []
    for item in qs:
        placemarks.append( kml_placemark(item) )
    dict['placemarks'] = placemarks
    from django.template import Context, Template
    from django.template.loader import get_template
    t = get_template('pg_spacing/general.kml')
    response = t.render(Context({ 'kml': dict }))
    return response

def kml_placemark(qs_item, styleUrl='#default', geo_field='geometry'):
    geom = qs_item.__getattribute__(geo_field)
    geom.transform(4326)
    try:
        name = qs_item.name
    except AttributeError:
        name = qs_item.model.__name__
    name = '<Name>%s</Name>' % name
    
    style = '<styleUrl>%s</styleUrl>' % styleUrl
    return_kml = '<Placemark>%s%s%s</Placemark>' % (name,style,geom.kml)
    return return_kml

class Land(models.Model): #may want to simplify geometry before storing in this table
    name = models.TextField(null=True, blank=True)
    geometry = models.PolygonField(srid=3310,null=True, blank=True)
    objects = models.GeoManager()
    
def add_geometry_to_network(qs):
    # gather polygon vertices from a query set (qs) and add the lines connecting those vertices that do not intersect
    # the geometries within the qs to the Network models.  This will typically be used with Land.objects.all() as the 
    # qs but I decided to make it more general.
    coords = ()
    for item in qs:
        coords += item.geometry.exterior_ring.coords
    points = [geos.Point(p) for p in coords]
    matrix = []
    for point in points:
        for pnt in points:
            if point <> pnt and (pnt,point) not in matrix: # if (1,2) has been dealt with, we don't need to consider (2,1)
                matrix.append( (point,pnt) )
                line = geos.MultiLineString( geos.LineString(point,pnt) )
                if not line_crosses_land(line,qs):
                    nw = Network(geometry=line)
                    nw.save()
                
def line_crosses_land(line,qs):
    crosses = False
    for l in qs:
        if line.intersects(l.geometry.buffer(-1)):
            crosses = True
    return crosses

class Network(models.Model):
    source = models.IntegerField(null=True,blank=True,db_index=True)
    target = models.IntegerField(null=True,blank=True,db_index=True)
    length = models.FloatField()
    geometry = models.MultiLineStringField(srid=3310)
    objects = models.GeoManager()
    
    def save(self):
        self.length = self.geometry.length
        super(Network,self).save()
        
def assign_vertex_ids(model=Network, tolerance=0.01, geometry_field='geometry', id_field='id'):
    db_table = model._meta.db_table
    cursor = connection.cursor()
    query_str = "SELECT assign_vertex_id('%s', %f, '%s', '%s')" % (db_table,tolerance,geometry_field,id_field)
    cursor.execute(query_str)
    cursor.db._commit()
    row = cursor.fetchone()
    return row