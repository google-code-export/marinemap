from django.contrib.gis.db import models
from django.contrib.gis.gdal import *
from django.contrib.gis import geos
from django.contrib.gis.measure import *
from django.template.defaultfilters import slugify
from osgeo import ogr
#from django.contrib.gis.utils import LayerMapping
import os
import tempfile
import zipfile
import glob

# I think I may be able to get rid of this because I'm using django file fields now
#DATA_PATH = os.path.join(os.path.dirname(__file__), 'data') #'C:/pydevWorkspace/reporting_dev/lingcod/intersection/data/' #

# Maybe these should go somewhere else?  Maybe get stored in a model?
LINEAR_OUT_UNITS = 'miles'
AREAL_OUT_UNITS = 'sq miles'
POINT_OUT_UNITS = 'count'

# I think this should stay here unless I want to pull some zip handling stuff into another app.
SHP_EXTENSIONS = ['shp','dbf','prj','sbn','sbx','shx','shp.xml','qix','fix']

def endswithshp(string):
    return string.endswith('.shp')
        
def zip_check(ext, zip_file):
    if not True in [info.filename.endswith(ext) for info in zip_file.infolist()]:
        return False
    return True
    
def validate_zipped_shp(file_path):
    # Just check to see if it's a valid zip and that it has the four necessary parts.
    # We're not checking to make sure it can be read as a shapefile  probably should somewhere.
    # We should also probably verify that the projection is what we expect.
    # I got a lot of this code from Dane Sprinmeyer's django-shapes app
    if not zipfile.is_zipfile(file_path):
        return False, 'That file is not a valid Zip Archive'
    else:
        zfile = zipfile.ZipFile(file_path)
    if not zip_check('shp', zfile):
        return False, 'Found Zip Archive but no file with a .shp extension found inside.'
    elif not zip_check('prj', zfile):
        return False, 'You must supply a .prj file with the Shapefile to indicate the projection.'
    elif not zip_check('dbf', zfile):
        return False, 'You must supply a .dbf file with the Shapefile to supply attribute data.'
    elif not zip_check('shx', zfile):
        return False, 'You must supply a .shx file for the Shapefile to have a valid index.'
    else:
        return True, None

def largest_poly_from_multi(geom):
    # takes a polygon or a multipolygon and returns only the largest polygon
    if geom.num_geom > 1:
        geom_area = 0.0
        for g in geom: # find the largest polygon in the multi polygon and use that
            if g.area > geom_area:
                the_one_true_geom = g
                geom_area = g.area
    else:
        the_one_true_geom = geom
    return the_one_true_geom

def clean_geometry(geom):
    from django.db import connection
    cursor = connection.cursor()
    query = "select cleangeometry(st_geomfromewkt(\'%s\')) as geometry" % geom.ewkt
    cursor.execute(query)
    row = cursor.fetchone()
    newgeom = geos.fromstr(row[0])
    # sometimes, clean returns a multipolygon
    geometry = largest_poly_from_multi(newgeom)
    
    if not geometry.valid or geometry.num_coords < 2:
        raise Exception("I can't clean this geometry. Dirty, filthy geometry. This geometry should be ashamed.")
    else:
        return geometry


def zip_from_shp(shp_path):
    # given a path to a '.shp' file, zip it and return the filename and a file object
    from django.core.files import File
    
    directory, file_with_ext = os.path.split(shp_path)
    if file_with_ext.count('.') <> 1:
        raise Exception('Shapefile name should only have one \'.\' in them.  This file name has %i.' % file_with_ext.count('.') )
    else:
        filename, ext = file_with_ext.split('.')
    zfile_path = os.path.join(directory, ('.').join([filename,'zip']) )    
    zfile = zipfile.ZipFile(zfile_path, 'w')
    for name in glob.glob( os.path.join(directory,filename + '.*') ):
        bn = os.path.basename(name)
        part_filenam, part_ext = bn.split('.',1)
        # make sure we're only adding allowed shapefile extensions
        if part_ext in SHP_EXTENSIONS:
            zfile.write(name, bn, zipfile.ZIP_DEFLATED)
    zfile.close()
    
    return filename, File( open(zfile_path) )

def sum_results(results):
    '''Sum a matrix of intersection results appropriately.  
    
    Here's an example of a data structure that can be summed
    [[{'feature_name': u'test points',
      'percent_of_total': 20.0,
      'result': 2.0,
      'sort': 0.5,
      'units': u'count'},
     {'feature_name': u'Beaches',
      'percent_of_total': 0.40000000000000002,
      'result': 2.0,
      'sort': 0.59999999999999998,
      'units': u'miles'},
     {'feature_name': u'Rocky Shores',
      'percent_of_total': 3.0,
      'result': 30.0,
      'sort': 0.69999999999999996,
      'units': u'miles'}],
      [{'feature_name': u'test points',
      'percent_of_total': 20.0,
      'result': 2.0,
      'sort': 0.5,
      'units': u'count'},
     {'feature_name': u'Beaches',
      'percent_of_total': 0.40000000000000002,
      'result': 2.0,
      'sort': 0.59999999999999998,
      'units': u'miles'},
     {'feature_name': u'Rocky Shores',
      'percent_of_total': 3.0,
      'result': 30.0,
      'sort': 0.69999999999999996,
      'units': u'miles'}]]
    '''
    # These keys will be summed.  Any other key will be the last value encountered.
    sum_keys_dict = {'result': 0.0,'percent_of_total': 0.0,'geo_collection': geos.fromstr('GEOMETRYCOLLECTION EMPTY') }
    sum_keys = sum_keys_dict.keys()
    
    summed_results = []
    for hab in range(0,results[0].__len__()):
        dict = {}
        # set up initial values
        for key in sum_keys: dict[key]=sum_keys_dict[key]
        for i in range(0,results.__len__()):
            for key in results[i][hab].keys():
                if key in sum_keys:
                    dict[key] += results[i][hab][key]
                elif key=='kml':
                    raise Exception("I haven't figured out how to sum kml so don't ask for kml when getting intersection results for Geometry collections")
                else:
                    if i <> 0:
                        # Since we're not summing these values, let's make sure they're actually the same.
                        try: assert(dict[key]==results[i][hab][key]) #print '%s = %s' % (dict[key], results[i][hab][key]) 
                        except: raise Exception('sum_results has been passed an incorrect results matrix.')
                    dict[key] = results[i][hab][key]
        summed_results.append(dict)
    return summed_results
    
class Shapefile(models.Model):
    #shapefile = models.FileField(upload_to='intersection/shapefiles')
    name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
#    def save(self, *args, **kwargs):
#        super(Shapefile, self).save(*args, **kwargs)
#        self.metadata = self.read_xml_metadata()
#        super(Shapefile, self).save(*args, **kwargs)
        
    def unzip_to_temp(self):
        # unzip to a temp directory and return the path to the .shp file
        valid, error = validate_zipped_shp(self.shapefile.path)
        if not valid:
            raise Exception(error)
        
        tmpdir = tempfile.gettempdir()
        zfile = zipfile.ZipFile(self.shapefile.path)
        for info in zfile.infolist():
            data = zfile.read(info.filename)
            if not info.filename[-1]==os.path.sep and not info.filename.startswith('__MACOSX'):
                shp_part = os.path.join(tmpdir, info.filename.split(os.path.sep)[-1])             
                fout = open(shp_part, "wb")
                fout.write(data)
                fout.close()
                if shp_part.endswith('.shp'):
                    shp_file = shp_part
        return shp_file
    
    def read_xml_metadata(self):
        shpfile = self.unzip_to_temp()
        xmlfile = shpfile + '.xml'
        if os.path.exists(xmlfile):
            f = open(xmlfile,'r')
            xml_text = f.readlines()
            f.close()
        else:
            xml_text = None
        return xml_text
    
    def field_info(self):
        fpath = self.unzip_to_temp()
        result = {}
        ds = DataSource(fpath)
        lyr = ds[0]
        field_names = lyr.fields
        for fname in field_names:
            field = lyr.get_fields(fname)
            distinct_values_count = dict.fromkeys(field).keys().__len__()
            result[fname] = distinct_values_count
        return result
        
class MultiFeatureShapefile(Shapefile):
    # These shape files may contain geometries that we want to turn into multiple intersection features.
    # An example would be the ESI shoreline layer.  It contains a line that is classified into many different
    # habitat types.
    shapefile = models.FileField(upload_to='intersection/shapefiles/multifeature')
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        super(MultiFeatureShapefile, self).save()
        self.link_field_names()
    
    def link_field_names(self):
        info_dict = self.field_info()
        for f in info_dict.keys():
            sf = ShapefileField(name=f,distinct_values=info_dict[f],shapefile=self)
            sf.save()
            
    def split_to_single_feature_shapefiles(self, field_name):
        file_path = self.unzip_to_temp()
        ds = DataSource(file_path)
        lyr = ds[0]
        if field_name not in lyr.fields:
            raise Exception('Specified field (%s) not found in %s' % (field_name,file_name) )
        field = lyr.get_fields(field_name)
        distinct_values = dict.fromkeys(field).keys()
        
        for dv in distinct_values:
            new_name, file = self.single_shapefile_from_field_value(field_name, dv)
            sfsf, created = SingleFeatureShapefile.objects.get_or_create(name=dv)
            if not created: #get rid of the old shapefile so it's not hangin around
                sfsf.shapefile.delete()
            sfsf.shapefile = file
#            if os.path.exists(sfsf.shapefile.path):
#                os.remove(sfsf.shapefile.path)
            sfsf.parent_shapefile = self
            sfsf.save()
            
    def single_shapefile_from_field_value(self, field_name, field_value):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        shpfile = self.unzip_to_temp()
        tempdir = tempfile.gettempdir()
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
        fn = str(os.path.abspath(os.path.join(tempdir, fn)))
        
        if os.path.exists(fn):
          driver.DeleteDataSource(fn)
        ds_out = driver.CreateDataSource(fn)
        if ds_out is None:
          raise 'Could not create file: %s' % fn
        
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
        fn_prj = slugify(field_value) + '.prj'
        fn_prj = str(os.path.abspath(os.path.join(tempdir, fn_prj)))
        file = open(fn_prj,'w')
        spatial_ref.MorphToESRI()
        file.write(spatial_ref.ExportToWkt())
        file.close()
        
        ds_in.Destroy()
        ds_out.Destroy()
        
        return zip_from_shp(fn)
    
class SingleFeatureShapefile(Shapefile):
    # These shape files contain geometries that represent only one intersection feature.
    shapefile = models.FileField(upload_to='intersection/shapefiles/singlefeature')
    parent_shapefile = models.ForeignKey(MultiFeatureShapefile, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    def load_to_features(self, verbose=False):
        ## This method loads individual features (with polygon, linestring, or point geometry) into
        # the appropriate model and loads relevant data 
        
        shpfile = self.unzip_to_temp()
        file_name = os.path.basename(shpfile)
        feature_name = self.name
        ds = DataSource(shpfile)
        #Data source objects can have different layers of geospatial features; however, 
        #shapefiles are only allowed to have one layer
        lyr = ds[0] 
        
        # make or update the intersection feature in the IntersectionFeature model
        try:
            intersection_feature = IntersectionFeature.objects.get(name=feature_name)
            created = False
        except IntersectionFeature.DoesNotExist:
            intersection_feature = IntersectionFeature(name=feature_name)
            created = True

        intersection_feature.native_units = lyr.srs.units[1]
        intersection_feature.save() # we need the pk value
        if created:
            intersection_feature = IntersectionFeature.objects.get(name=feature_name)
        
        ds = DataSource(shpfile)
        lyr = ds[0]
        if lyr.geom_type=='LineString':
            feature_model = LinearFeature
            out_units = LINEAR_OUT_UNITS
            #mgeom = geos.fromstr('MULTILINESTRING EMPTY')
        elif lyr.geom_type=='Polygon':
            feature_model = ArealFeature
            out_units = AREAL_OUT_UNITS
            intersection_feature.native_units = 'Sq ' + intersection_feature.native_units
            #mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
        elif lyr.geom_type=='Point':
            feature_model = PointFeature
            out_units = POINT_OUT_UNITS
            #mgeom = geos.fromstr('MULTILIPOINT EMPTY')
        else:
            raise 'Unrecognized type for load_features.'
        
        # get rid of old stuff if it's there
        feature_model.objects.filter(feature_type=intersection_feature).delete()
        
        if verbose:
            print 'Loading %s from %s' % (feature_name,file_name)
        
        area = 0.0
        length = 0.0
        count = 0
        
        for feat in lyr:
            if feat.geom.__class__.__name__.startswith('Multi'):
                if verbose:
                    print '(',
                for f in feat.geom: #get the individual geometries
                    fm = feature_model(name=feature_name,feature_type=intersection_feature)
                    fm.geometry = f.geos
                    if not fm.geometry.valid:
                        fm.geometry = clean_geometry(fm.geometry)
                    #mgeom.append(fm.geometry)
                    if out_units==AREAL_OUT_UNITS:
                        area += fm.geometry.area
                    elif out_units==LINEAR_OUT_UNITS:
                        length += fm.geometry.length
                    else:
                        count += 1
                    fm.save()
                    if verbose:
                        print '-',
                if verbose:
                    print ')',
            else:
                fm = feature_model(name=feature_name,feature_type=intersection_feature)
                fm.geometry = feat.geom.geos
                if not fm.geometry.valid:
                    fm.geometry = clean_geometry(fm.geometry)
                #mgeom.append(fm.geometry)
                if out_units==AREAL_OUT_UNITS:
                    area += fm.geometry.area
                elif out_units==LINEAR_OUT_UNITS:
                    length += fm.geometry.length
                else:
                    count += 1
                fm.save()
                if verbose:
                    print '.',
        
        
        if out_units==AREAL_OUT_UNITS:
            intersection_feature.study_region_total = A(sq_m=area).sq_mi
        elif out_units==LINEAR_OUT_UNITS:
            intersection_feature.study_region_total = D(m=length).mi
        else:
            intersection_feature.study_region_total = count
        intersection_feature.output_units = out_units
        intersection_feature.shapefile = self
        intersection_feature.multi_shapefile = self.parent_shapefile
        intersection_feature.feature_model = feature_model.__name__
        intersection_feature.save()
    
class ShapefileField(models.Model):
    # We'll need information about the fields of multi feature shapefiles so we can turn them into single feature shapefiles
    name = models.CharField(max_length=255)
    distinct_values = models.IntegerField()
    type = models.CharField(max_length=255, null=True, blank=True)
    shapefile = models.ForeignKey(MultiFeatureShapefile)
    
    def __unicode__(self):
        return self.name

class TestPolygon(models.Model):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()

class IntersectionFeature(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    study_region_total = models.FloatField(null=True, blank=True, help_text="This is the quantity of this habitat type available within the study region. This value will be generated programmatically and should not be manually altered")
    native_units = models.CharField(max_length=255,null=True, blank=True, help_text="Units native to this layer's projection.")
    output_units = models.CharField(max_length=255,null=True, blank=True, help_text="Unit label to be displayed after results from this table.")
    #shapefile_name = models.TextField(null=True, blank=True, help_text="The name of the shapefile that was imported to the database.")
    shapefile = models.ForeignKey(SingleFeatureShapefile, null=True)
    multi_shapefile = models.ForeignKey(MultiFeatureShapefile,null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    TYPE_CHOICES = (
                    ('ArealFeature', 'Areal'),
                    ('LinearFeature', 'Linear'),
                    ('PointFeature', 'Point'),
                   )
    feature_model = models.CharField(null=True, blank=True, max_length=20, choices=TYPE_CHOICES)
#    geometry_line = models.MultiLineStringField(null=True, blank=True, srid=3310)
#    geometry_poly = models.MultiPolygonField(null=True, blank=True, srid=3310)
#    geometry_point = models.MultiPointField(null=True, blank=True, srid=3310)
    objects = models.GeoManager()
   
    def __unicode__(self):
        return self.name
    
    def save(self):
        self.expire_cached_results()
        super(IntersectionFeature,self).save()
    
    @property
    def model_with_my_geometries(self):
        appname = os.path.dirname(__file__).split(os.path.sep).pop()
        model_with_geom = models.get_model(appname,self.feature_model)
        return model_with_geom
    
    @property
    def geometry(self):
        # Returns a multigeometry of the appropriate type containing all geometries for this intersection feature.
        # Don't bother to call this on the large polygon features.  It takes far too long.
        individual_features = self.model_with_my_geometries.objects.filter(feature_type=self)
        
        if model_with_my_geometries==ArealFeature:
            mgeom = geos.fromstr('MULTIPOLYGON EMPTY')
        elif model_with_my_geometries==LinearFeature:
            mgeom = geos.fromstr('MULTILINESTRING EMPTY')
        elif model_with_my_geometries==PointFeature:
            mgeom = geos.fromstr('MULTIPOINT EMPTY')
        else:
            raise 'Could not figure out what geometry type to use.'
        
        if individual_features:
            for feature in individual_features:
                mgeom.append(feature.geometry)
        return mgeom
    
    @property
    def geometries_set(self):
        # Returns a query set of all the ArealFeature, LinearFeature, or PointFeature objects related to this intersection feature.
        return self.model_with_my_geometries.objects.filter(feature_type=self)
    
    def expire_cached_results(self):
        self.resultcache_set.all().delete()

class OrganizationScheme(models.Model):
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    @property
    def info(self):
        subdict = {}
        subdict['name'] = self.name
        subdict['pk'] = self.pk
        subdict['num_features'] = self.featuremapping_set.all().count()
        feature_dict = {}
        for f in self.featuremapping_set.all().order_by('sort'):
            feature_dict[f.name] = f.units
        subdict['feature_names_units'] = feature_dict
        return subdict
    
    def validate(self):
        for fm in self.featuremapping_set.all():
            if not fm.validate(quiet=True):
                return False
        return True
    
    def transformed_results(self, geom_or_collection, with_geometries=False, with_kml=False):
        if geom_or_collection.geom_type.lower().endswith('polygon'):
            return self.transformed_results_single_geom(geom_or_collection, with_geometries=with_geometries, with_kml=with_kml)
        elif geom_or_collection.geom_type.lower().endswith('collection'):
            #do stuff for a collection
            results_matrix = []
            for geom in geom_or_collection:
                geom_results = self.transformed_results_single_geom(geom, with_geometries=with_geometries, with_kml=with_kml)
                results_matrix.append(geom_results)
            summed_results = sum_results(results_matrix)
            return summed_results
        else:
            raise Exception('transformed results only available for Polygons and geometry collections.  something else was submitted.')
    
    def transformed_results_single_geom(self, geom, with_geometries=False, with_kml=False):
        new_results = []
        for fm in self.featuremapping_set.all():
            dict = {}
            #features = fm.feature.all()
            dict['feature_name'] = fm.name
            feature_pks = [f.pk for f in fm.feature.all()]
            results = intersect_the_features(geom, feature_list=feature_pks, with_geometries=with_geometries or with_kml, with_kml=with_kml)
            intersection_total = 0.0
            sr_total = 0.0
            if with_geometries or with_kml:
                f_gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
            for pk in feature_pks:
                for result in results:
                    if result['hab_id']==pk:
                        intersection_total += result['result']
                        #percent_sr_total += result['percent_of_total'] #wrong, can't add these percentages up have to determine total/total available
                        sr_total += IntersectionFeature.objects.get(pk=pk).study_region_total
                        if with_geometries or with_kml:
                            f_gc = f_gc + result['geo_collection']
            dict['result'] = intersection_total
            dict['percent_of_total'] = (intersection_total / sr_total) * 100
            dict['sort'] = fm.sort
            dict['units'] = fm.feature.all()[0].output_units
            if with_geometries:
                dict['geo_collection'] = f_gc
            if with_kml:
                dict['kml'] = f_gc.kml
            new_results.append(dict)
        
        return new_results
            
    
class FeatureMapping(models.Model):
    organization_scheme = models.ForeignKey(OrganizationScheme)
    feature = models.ManyToManyField(IntersectionFeature)
    name = models.CharField(max_length=255)
    sort = models.FloatField()    
    
    class Meta:
        ordering = ('sort','name')
    
    def __unicode__(self):
        return self.name  
    
    @property
    def study_region_total(self):
        total = 0.0
        for feature in self.feature.all():
            total += feature.study_region_total
        return total
    
    @property
    def units(self):
        if self.validate():
            return self.feature.all()[0].output_units
        
    @property
    def type(self):
        if self.validate():
            return self.feature.all()[0].feature_model.lower().replace('feature','')
    
    def validate(self, quiet=False):
        if self.validate_feature_count(quiet) and self.validate_type(quiet) and self.validate_units(quiet):
            return True
        else:
            return False
    
    def validate_feature_count(self, quiet=False):
        if self.feature.all().count() < 1:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme has no features.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
    
    def validate_units(self, quiet=False):
        # Make sure that if there are multiple features to be combined that they all have the 
        # same units.
        units = self.feature.all()[0].output_units
        if False in [units==f.output_units for f in self.feature.all()]:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme combines features with different units.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
    
    def validate_type(self, quiet=False):
        # Make sure that if there are multiple features to be combined that they all have the 
        # same type.
        type = self.feature.all()[0].feature_model
        if False in [type==f.feature_model for f in self.feature.all()]:
            if quiet:
                return False
            else:
                error = '%s in %s organization scheme combines different types of features.' % (self.name, self.organization_scheme.name)
                raise Exception(error)
        else:
            return True
        
#    def save(self):
#        super(FeatureMapping,self).save()
#        pk = self.pk
#        if not self.validate():
#            self.delete()
#            raise Exception('You can not combine feature types with different output units.  That just would not make any sense, would it?')
#        else:
#            super(FeatureMapping,self).save()
    
class CommonFeatureInfo(models.Model):
    name = models.CharField(max_length=255)
    feature_type = models.ForeignKey(IntersectionFeature)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True) # updating also handled by a trigger defined in lingcod/intersection/sql. manage.py creates the trigger.  This will let us modify features in qgis if we need to and still know when features were updated.
    objects = models.GeoManager()
    
    class Meta:
        abstract = True
        
class ArealFeature(CommonFeatureInfo):
    geometry = models.PolygonField(srid=3310)
    objects = models.GeoManager()
    
    def intersection(self,geom):
        return self.geometry.intersection(geom)
    
class LinearFeature(CommonFeatureInfo):
    geometry = models.LineStringField(srid=3310)
    objects = models.GeoManager()
    
    def intersection(self,geom):
        return self.geometry.intersection(geom)
    
class PointFeature(CommonFeatureInfo):
    geometry = models.PointField(srid=3310)
    objects = models.GeoManager()
    
class ResultCache(models.Model):
    wkt_hash = models.CharField(max_length=255)
    intersection_feature = models.ForeignKey(IntersectionFeature)
    result = models.FloatField()
    units = models.CharField(max_length=255)
    percent_of_total = models.FloatField()
    date_modified = models.DateTimeField(auto_now=True)
    geometry = models.GeometryCollectionField()
    objects = models.GeoManager()
    
def intersect_the_features(geom, feature_list=None, with_geometries=False, with_kml=False):
    # if no feature list is specified, get all the features
    if not feature_list:
        feature_list = [i.pk for i in IntersectionFeature.objects.all()]
    dict_list = []
    for f_pk in feature_list:
        dict = {}
        f_gc = geos.fromstr('GEOMETRYCOLLECTION EMPTY')
        int_feature = IntersectionFeature.objects.get(pk=f_pk)
        dict['hab_id'] = f_pk
        dict['feature_name'] = int_feature.name
        dict['units'] = int_feature.output_units
        try: # get results from cache if they're there
            rc = ResultCache.objects.get( wkt_hash=str(geom.wkt.__hash__()), intersection_feature=int_feature )
            dict['result'] = rc.result
            dict['percent_of_total'] = rc.percent_of_total
            if with_geometries:
                dict['geo_collection'] = rc.geometry
            if with_kml:
                dict['kml'] = rc.geometry.kml 
                
        except ResultCache.DoesNotExist: # Calculate if cached results doen't exist
            if not int_feature.feature_model=='PointFeature':
                geom_set = int_feature.geometries_set.filter(geometry__intersects=geom)
                for g in geom_set:
                    intersect_geom = geom.intersection(g.geometry)
                    geom_area = geom.area
                    f_gc.append(intersect_geom)
            else:
                geom_set = int_feature.geometries_set.filter(geometry__within=geom)
                for p in geom_set:
                    f_gc.append(p.geometry)
                
            if with_geometries:
                dict['geo_collection'] = f_gc
            if with_kml:
                dict['kml'] = f_gc.kml    
                
            if int_feature.feature_model=='ArealFeature':
                dict['result'] = A(sq_m=f_gc.area).sq_mi
            elif int_feature.feature_model=='LinearFeature':
                dict['result'] = D(m=f_gc.length).mi
            elif int_feature.feature_model=='PointFeature':
                dict['result'] = f_gc.num_geom
                
            dict['percent_of_total'] = (dict['result'] / int_feature.study_region_total) * 100
            
            # Cache the results we've calculated
            rc = ResultCache( wkt_hash=geom.wkt.__hash__(), intersection_feature=int_feature )
            rc.result = dict['result']
            rc.units = int_feature.output_units
            rc.percent_of_total = dict['percent_of_total']
            rc.geometry = f_gc
            rc.save()
            
        dict_list.append(dict)
    return dict_list
    
