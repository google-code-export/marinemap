from django.test import TestCase
from lingcod.intersection.admin import *
from lingcod.intersection.models import *
import os

class AddFeaturesTest(TestCase):
    def test_upload_multifeature_shapefiles(self):
        """
        Make sure we can upload multifeature shapefiles
        """
        fixtures = ['test_data.json']
        self.client.get('/admin/')
        response = self.client.post('/admin/', { 'username' : 'test', 'password' : 'testing', 'this_is_the_login_form' : 1, 'submit' : 'Log in' } )
        print response
        linear_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'hab_shoretype_srsc.zip')
        linear_zip = open(linear_zip_path)
        #form = MultiFeatureShapefileAdmin.form
        response = self.client.post('/admin/intersection/multifeatureshapefile/add/', { 'shapefile' : linear_zip, 'name' : 'test linear' })
        print response
        self.failUnlessEqual(response.status_code, 200)
        
    
        if MultiFeatureShapefile.objects.all().count() > 0:
            it_is = True
        else:
            it_is = False
        self.failUnlessEqual(it_is,True)



