from django.contrib.gis.db import models
from django.contrib.gis.gdal import *
from django.template.defaultfilters import slugify
from osgeo import ogr
#from django.contrib.gis.utils import LayerMapping
import os

DATA_PATH = 'C:/pydevWorkspace/reporting_dev/lingcod/intersection/data/' #os.path.join(os.path.dirname(__file__), 'data')

def load_features(file_name, feature_name, verbose=True):
    ## TO DO: fill out intersection_feature attributes when updating that record
    
    shpfile = os.path.abspath(os.path.join(DATA_PATH, file_name))
    #shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', file_name))
    ds = DataSource(shpfile)
    #Data source objects can have different layers of geospatial features; however, 
    #shapefiles are only allowed to have one layer
    lyr = ds[0] 
    
    # make or update the intersection feature in the IntersectionFeature model
    intersection_feature, created = IntersectionFeature.objects.get_or_create(name=feature_name)
    intersection_feature.native_units = lyr.srs.units[1]
    intersection_feature.save() # we need the pk value
    if created:
        intersection_feature = IntersectionFeature.objects.get(name=feature_name)
    
    ds = DataSource(shpfile)
    lyr = ds[0]
    if lyr.geom_type=='LineString':
        feature_model = LinearFeature
    elif lyr.geom_type=='Polygon':
        feature_model = ArealFeature
    elif lyr.geom_type=='Point':
        feature_model = PointFeature
    else:
        raise 'Unrecognized type for load_features.'
    
    # get rid of old stuff if it's there
    feature_model.objects.filter(feature_type=intersection_feature).delete()
    
    for feat in lyr:
        if feat.geom.__class__.__name__.startswith('Multi'):
            if verbose:
                print '(',
            for f in feat.geom: #get the individual geometries
                fm = feature_model(name=feature_name,feature_type=intersection_feature)
                fm.geometry = f.geos
                fm.save()
                if verbose:
                    print '-',
            if verbose:
                print ')',
        else:
            fm = feature_model(name=feature_name,feature_type=intersection_feature)
            fm.geometry = feat.geom.geos
            fm.save()
            if verbose:
                print '.',
    
    ds.Destroy()
                
def shapefile_from_field_value(file_name, field_name, field_value):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shpfile = os.path.abspath(os.path.join(DATA_PATH, file_name))
    #open input data source
    ds_in = driver.Open(shpfile,0)
    if ds_in is None:
        raise 'Could not open input shapefile'
    lyr_in = ds_in.GetLayer()
    
    #determine what geometry type we're dealing with
    feat = lyr_in.GetFeature(0)
    geom = feat.GetGeometryRef()
    gname = geom.GetGeometryName()
        
    # create a new data source and layer
    fn = slugify(field_value) + '.shp'
    fn = str(os.path.abspath(os.path.join(DATA_PATH, fn)))
    print fn
    if os.path.exists(fn):
      driver.DeleteDataSource(fn)
    ds_out = driver.CreateDataSource(fn)
    if ds_out is None:
      raise 'Could not create file'
    
    if gname.lower().endswith('polygon'):
        geometry_type = ogr.wkbMultiPolygon
    elif gname.lower().endswith('linestring'):
        geometry_type = ogr.wkbMultiLineString
    elif gname.lower().endswith('linestring'):
        geometry_type = ogr.wkbMultiPoint
    else:
        raise 'Unregonized geometry type'
    
    lyr_out = ds_out.CreateLayer(str(slugify(field_value)), geom_type=geometry_type)
    
    # get the FieldDefn's for the fields in the input shapefile
    transferFieldDefn = feat.GetFieldDefnRef(field_name)
    
    #create new fields in the output shapefile
    lyr_out.CreateField(transferFieldDefn)
    
    #get the FeatureDefn for the output
    feat_defn = lyr_out.GetLayerDefn()
    
    # loop through the input features
    feat_in = lyr_in.GetNextFeature()
    while feat_in:
        field = feat_in.GetField(field_name)
        
        if field==field_value:
            # create new feature
            feat_out = ogr.Feature(feat_defn)
            #set the geometry
            geom_in = feat_in.GetGeometryRef()
            feat_out.SetGeometry(geom_in)
            #set the attributes
            id = feat_in.GetFID()
            feat_out.SetFID(id)
            feat_out.SetField(field_name,field)
            # add the feature to the ouput layer
            lyr_out.CreateFeature(feat_out)
            # destroy the output feature
            feat_out.Destroy()
        
        #destroy the input feature and get a new one
        feat_in.Destroy()
        feat_in = lyr_in.GetNextFeature()
    
    # get the projection from the input shapefile and write a .prj file for the output
    spatial_ref = lyr_in.GetSpatialRef()
    fn = slugify(field_value) + '.prj'
    fn = str(os.path.abspath(os.path.join(DATA_PATH, fn)))
    file = open(fn,'w')
    spatial_ref.MorphToESRI()
    file.write(spatial_ref.ExportToWkt())
    file.close()
    
    ds_in.Destroy()
    ds_out.Destroy()
    

def prep_layer_mapping(shpfile_name, model, mapping):
    shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', shpfile_name))
    lm = LayerMapping(model, shpfile, mapping, transform=False, encoding='iso-8859-1')
    return lm

class IntersectionFeature(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    study_region_total = models.FloatField(null=True, blank=True, help_text="This is the linear quantity of this habitat type available within the study region. This value will be generated programmatically and should not be manually altered")
    native_units = models.TextField(null=True, blank=True, help_text="Units native to this layer's projection.")
    output_units = models.TextField(null=True, blank=True, help_text="Unit label to be displayed after results from this table.")
    shapefile_name = models.TextField(null=True, blank=True, help_text="The name of the shapefile that was imported to the database.")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    TYPE_CHOICES = (
                    ('ArealFeature', 'Areal'),
                    ('LinearFeature', 'Linear'),
                    ('PointFeature', 'Point'),
                   )
    feature_model = models.CharField(null=True, blank=True, max_length=10, choices=TYPE_CHOICES)
    geometry_line = models.MultiLineStringField(null=True, blank=True, srid=3310)
    geometry_poly = models.MultiPolygonField(null=True, blank=True, srid=3310)
    geometry_point = models.MultiPointField(null=True, blank=True, srid=3310)
    objects = models.GeoManager()
   
    def __unicode__(self):
        return self.name
    
class CommonFeatureInfo(models.Model):
    name = models.CharField(max_length=255)
    feature_type = models.ForeignKey(IntersectionFeature)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True) # updating this is taken care of by a trigger defined in lingcod/intersection/sql. manage.py creates the trigger.  This will let us modify features in qgis if we need to and still know when features were updated.  heeeelll yeah.
    objects = models.GeoManager()
    
    class Meta:
        abstract = True
        
class ArealFeature(CommonFeatureInfo):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()
    
class LinearFeature(CommonFeatureInfo):
    geometry = models.LineStringField(srid=3310)
    objects = models.GeoManager()
    
class PointFeature(CommonFeatureInfo):
    geometry = models.PointField(srid=3310)
    objects = models.GeoManager()