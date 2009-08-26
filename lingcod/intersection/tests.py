from django.test import TestCase
from lingcod.intersection.admin import *
from lingcod.intersection.models import *
import os

class UploadShapefilesTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
            
    def tearDown(self):
        # The tests should delete these but just in case they don't they're deleted here
        # If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
    
    def test_multishapefile_upload(self):
        # upload polygon shapefile
        polygon_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_substrate.zip')
        polygon_zip = open(polygon_zip_path)
        form_data = { 'shapefile' : polygon_zip, 'name' : 'test polygon', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', form_data)
        polygon_zip.close()
        #print response
        self.assertRedirects(response, '/admin/intersection/multifeatureshapefile/')
        
        # Check to make sure the shapefile has been added
        mfs = MultiFeatureShapefile.objects.get(name='test polygon')
        if mfs:
            it_is = True
        else:
            it_is = False
        self.assertTrue(it_is)
        # make sure the file has been put where it's supposed to be
        file_path = mfs.shapefile.path
        self.assertTrue( os.path.exists(file_path) )
        # make sure the file goes away when the feature is deleted
        mfs.delete()
        self.assertFalse( os.path.exists(file_path) )
        
    def test_singleshapefile_upload(self):
        # upload point shapefile
        point_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_points.zip')
        point_zip = open(point_zip_path)
        form_data = { 'shapefile' : point_zip, 'name' : 'test points', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/singlefeatureshapefile/add/', form_data)
        point_zip.close()
        #print response
        self.assertRedirects(response, '/admin/intersection/singlefeatureshapefile/')
        
        # Check to make sure the shapefile has been added
        sfs = SingleFeatureShapefile.objects.get(name='test points')
        if sfs:
            it_is = True
        else:
            it_is = False
        self.assertTrue(it_is)
        # make sure the file has been put where it's supposed to be
        file_path = sfs.shapefile.path
        self.assertTrue( os.path.exists(file_path) )
        # make sure the file goes away when the feature is deleted
        sfs.delete()
        self.assertFalse( os.path.exists(file_path) )
        
class SplitToSingleFeatureShapefilesTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
        # upload polygon shapefile
        polygon_zip = open( os.path.join(os.path.dirname(__file__), 'test_data', 'test_substrate.zip') )
        form_data = { 'shapefile' : polygon_zip, 'name' : 'test polygon', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', form_data)
        polygon_zip.close()
        mfs_poly = MultiFeatureShapefile.objects.get(name='test polygon')
        
        # upload a linear shapefile
        linear_zip = open( os.path.join(os.path.dirname(__file__), 'test_data', 'test_shoretype.zip') )
        form_data = { 'shapefile' : linear_zip, 'name' : 'test linear', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', form_data)
        linear_zip.close()
        mfs_line = MultiFeatureShapefile.objects.get(name='test linear')
        
        
    def tearDown(self):
#         The tests should delete these but just in case they don't they're deleted here
#         If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
        
    def test_poly_multi_split_to_single(self):
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test polygon').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'sub_depth' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        self.assertRedirects(response, '/admin/intersection/singlefeatureshapefile/')
        self.assertEquals( SingleFeatureShapefile.objects.all().count(), 11)
        for sfs in SingleFeatureShapefile.objects.filter(parent_shapefile=MultiFeatureShapefile.objects.get(name='test polygon')):
            # make sure the file is where it's supposed to be
            file_path = sfs.shapefile.path
            self.assertTrue( os.path.exists(file_path) )
            # make sure the file goes away when the feature is deleted
            sfs.delete()
            self.assertFalse( os.path.exists(file_path) )
            
    def test_linear_multi_split_to_single(self):
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test linear').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'mapclass' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        self.assertRedirects(response, '/admin/intersection/singlefeatureshapefile/')
        self.assertEquals( SingleFeatureShapefile.objects.all().count(), 2)
        for sfs in SingleFeatureShapefile.objects.all():
            # make sure the file is where it's supposed to be
            file_path = sfs.shapefile.path
            self.assertTrue( os.path.exists(file_path) )
            # make sure the file goes away when the feature is deleted
            sfs.delete()
            self.assertFalse( os.path.exists(file_path) )
            
class ImportShapefileFeaturesToDbTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
        # upload polygon shapefile
        polygon_zip = open( os.path.join(os.path.dirname(__file__), 'test_data', 'test_substrate.zip') )
        form_data = { 'shapefile' : polygon_zip, 'name' : 'test polygon', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', form_data)
        polygon_zip.close()
        mfs_poly = MultiFeatureShapefile.objects.get(name='test polygon')
        
        # upload a linear shapefile
        linear_zip = open( os.path.join(os.path.dirname(__file__), 'test_data', 'test_shoretype.zip') )
        form_data = { 'shapefile' : linear_zip, 'name' : 'test linear', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', form_data)
        linear_zip.close()
        mfs_line = MultiFeatureShapefile.objects.get(name='test linear')
        
        # split polygon multi features into single feature shapefiles
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test polygon').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'sub_depth' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        
        # split linear multi features in single feature shapefiles
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test linear').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'mapclass' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        
        # upload point shapefile
        point_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_points.zip')
        point_zip = open(point_zip_path)
        form_data = { 'shapefile' : point_zip, 'name' : 'test points', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/singlefeatureshapefile/add/', form_data)
        point_zip.close()
        
    def tearDown(self):
#         The tests should delete these but just in case they don't they're deleted here
#         If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
        
    def test_shapefiles_to_features(self):
        for shape in SingleFeatureShapefile.objects.all():
            shape.load_to_features()
            # make sure features exist
            if IntersectionFeature.objects.filter(name=shape.name):
                result = True
                int_feat = IntersectionFeature.objects.get(name=shape.name)
            else:
                result = False
            self.assertTrue(result)
            if not result:
                return False
            
            # make sure that geometries exist for the feature
            geom_set = int_feat.geometries_set
            if geom_set:
                result = True
            else:
                result = False
            self.assertTrue(result)
            
class RunIntersectionsWithTestPolygonTest(TestCase):
    fixtures = ['with_test_data_loaded.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
            
    def test_default_intersection_with_test_polygon(self):
        import pickle
        
        tp = TestPolygon.objects.all()[0]
        result = intersect_the_features(tp.geometry)
        
        pickle_path = os.path.join(os.path.dirname(__file__), 'test_data', 'default_tp1_result.pickle')
        f = open(pickle_path, 'rb')
        pickled_result = pickle.load(f)
        f.close()
        
        keys = pickled_result[0].keys()
        for i in range(0,pickled_result.__len__() ):
            for key in keys:
                if key=='result' or key=='percent_of_total':
                    self.assertEqual(round(result[i][key],7),round(pickled_result[i][key],7))
                else:
                    self.assertEqual(result[i][key],pickled_result[i][key])
                       
    def test_ordered_intersection_with_test_polygon(self):
        import pickle
        
        osc = OrganizationScheme.objects.get(name='Nice Order')
        tp = TestPolygon.objects.all()[0]
        result = osc.transformed_results(tp.geometry)
        
        pickle_path = os.path.join(os.path.dirname(__file__), 'test_data', 'nice_order_tp1_result.pickle')
        f = open(pickle_path, 'rb')
        pickled_result = pickle.load(f)
        f.close()
        
        keys = pickled_result[0].keys()
        for i in range(0,pickled_result.__len__() ):
            for key in keys:
                if key=='result' or key=='percent_of_total':
                    self.assertEqual(round(result[i][key],7),round(pickled_result[i][key],7))
                else:
                    self.assertEqual(result[i][key],pickled_result[i][key])