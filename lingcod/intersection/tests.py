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
        point_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_substrate.zip')
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
        
        return mfs_poly, mfs_line
        
    def tearDown(self):
        # The tests should delete these but just in case they don't they're deleted here
        # If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
        
    def test_poly_multi_split_to_single(self):
        form_data = { 'mfshp_pk': 1, 'shp_field': 'sub_depth' }
        response = self.client.post('/admin/intersection/multifeatureshapefile/1/splitonfield/', form_data)
        self.assertRedirects(response, '/admin/intersection/singlefeatureshapefile/')
        self.assertEquals( SingleFeatureShapefile.objects.all().count(), 11)