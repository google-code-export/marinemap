"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from mlpa.models import *
from django.conf import settings
from django.conf.urls.defaults import *

from views import *
from django.contrib.gis.geos import *
from django.core import serializers

urlpatterns = patterns('',
    (r'/mlpa/', include('mlpa.urls')),
)


class MlpaTest(TestCase):
        
    def testKmlAllGeom(self):
        """
        test views.mpaKmlAllGeom
        """

        response = self.client.get('/mlpa/mpa/1/kmlAllGeom/', {})
        self.assertEquals(response.status_code, 200)
        
    def testKmlView(self):
        """
        test views.kml
        """
        response = self.client.get('/mlpa/mpa/1/kml/', {})
        self.assertEquals(response.status_code, 200)
        
    #def testExternalKmlStyle(self):
    #    response = self.client.get('/media/studyregion/styles.kml', {})
    #    self.assertEquals(response.status_code, 200)


class MlpaValidateTest(TestCase):
    '''
        Commands used to run the following test (from the python manage.py shell command line):
            from mlpa.tests import *
            tester = MlpaValidateTest('testManipulators')
            tester.setUp()
            tester.testManipulators()
            tester.tearDown()
        
        Or the following to run as unit test:
            python manage.py test mlpa
    '''

    def setUp(self):
        '''
            mpaValidate expected code_status results:
            code_status 0:  clips to study region, no estuary overlap
            code_status 1:  overlaps with estuary, oceanic part chosen
            code_status 2:  outside study region
            code_status 3:  geometry not valid
            code_status 4:  estuary only (currently not used in mpaVAlidate)
            code_status 5:  overlaps with estuary, estuary part chosen
            
            #code_status 6 is particular to manipulator classes
            code_status 6:  one or more required kwargs not provided
        '''
        
        self.code0_poly = fromstr('POLYGON ((-1 -1, 1 -1, 1 -3, -1 -3, -1 -1))') # area = 4
        self.code1_poly = fromstr('POLYGON ((-1 1, 1 1, 1 -1, -1 -1, -1 1))') # area = 4
        self.code2_poly = fromstr('POLYGON ((3 3, 4 3, 4 4, 3 4, 3 3))') # area = 1
        self.code3_poly = fromstr('POLYGON ((3 3, 4 3, 3 4, 4 4, 3 3))') # area = 0
        self.code4_poly = fromstr('POLYGON ((0 2, 1 0, 2 2, 0 2))') # area = 2
        self.code5_poly = fromstr('POLYGON ((0 2, 2 2, 2 1, 0 1, 0 2))') # area = 2
        
        self.study_region = fromstr('POLYGON ((-2 2, 2 2, 2 -2, -2 -2, -2 2))')
        
        self.est1 = fromstr('POLYGON ((0 2, 1 0, 2 2, 0 2))') # same as code4_poly
        self.est2 = fromstr('POLYGON ((0 2, -1 0, -2 2, 0 2))') # est1.area == est2.area == 2
        self.ests = MultiPolygon(self.est1, self.est2)
        self.ests.srid=900913
   
        self.client = Client()
        
    def tearDown(self):
    
        self.code0_poly = None
        self.code1_poly = None
        self.code2_poly = None
        self.code3_poly = None
        self.code4_poly = None
        self.code5_poly = None
        
        self.study_region = None
        
        self.est1 = None
        self.est2 = None
        self.ests = None
   
        self.client = None
        
    def testManipulators(self):
        #individual testing methods will be called from here    
        self.clipToGraticuleTest()
        self.clipToStudyRegionTest()
        self.clipToEstuariesTest()
        self.clipToNCMLPATest()
        
        
    #Clip To Graticule testing (similar testing is already done in manipulators.tests)
    def clipToGraticuleTest(self):
        '''
            Tests the following:
            code_status 0:  clipped to graticule
        '''
        #clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'w': .5, 'e': -.5})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '0')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, w=.5, e=-.5)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
    
    #Clip To Study Region testing (similar testing is already done in manipulators.tests)
    def clipToStudyRegionTest(self):
        '''
            Tests the following:
            code_status 0:  clipped to study region
            code_status 2:  outside study region
            code_status 3:  geometry not valid
        '''
        #clipped to study region
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code0_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response0.status_code, 200)
        json0 = serializers.json.simplejson.loads(response0.content)
        self.assertEquals(json0["status_code"], '0')
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=self.code0_poly, study_region=self.study_region)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        
        #outside study region
        response2 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code2_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response2.status_code, 200)
        json2 = serializers.json.simplejson.loads(response2.content)
        self.assertEquals(json2["status_code"], '2')
        
        #geometry not valid
        response3 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code3_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response3.status_code, 200)
        #json3 = serializers.json.simplejson.loads(response3.content)
        #self.assertEquals(json3["status_code"], '3')
    
    #Clip to Estuary Oceanic testing
    def clipToEstuariesTest(self):
        '''
            Tests the following:
            code_status 0:  no estuary overlap ('cliipped_shape == 'target_shape')
            code_status 1:  overlaps both estuary and oceanic, oceanic returned
            code_status 5:  overlaps both estuary and oceanic, estuary returned
            code_status 3:  geometry not valid
            code_status 4:  estuary only
            code_status 6:  missing kwargs
        '''
        #mpa does not overlap with estuary
        response0 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code0_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response0.status_code, 200)
        json0 = serializers.json.simplejson.loads(response0.content)
        self.assertEquals(json0["status_code"], '0')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=self.code0_poly, estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 4, places=1)
    
        #overlaps both estuary and oceanic, oceanic returned
        response1 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code1_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '1')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=self.code1_poly, estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '1')
        self.assertAlmostEquals(result["clipped_shape"].area, 3.5, places=1)
        
        #overlaps both estuary and oceanic, estuary returned
        response5 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code5_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response5.status_code, 200)
        json5 = serializers.json.simplejson.loads(response5.content)
        self.assertEquals(json5["status_code"], '5')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=self.code5_poly, estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '5')
        self.assertAlmostEquals(result["clipped_shape"].area, 1.5, places=1)
        
        #mpa is outside of study region (but this shouldn't matter much to ClipToEstuaries)
        response2 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code2_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response2.status_code, 200)
        json2 = serializers.json.simplejson.loads(response2.content)
        self.assertEquals(json2["status_code"], '0')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=self.code2_poly, estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 1, places=1)

        #mpa geometry is not valid
        response3 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code3_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response3.status_code, 200)
        json3 = serializers.json.simplejson.loads(response3.content)
        self.assertEquals(json3["status_code"], '3')
        self.assertEquals(json3["clipped_shape"], None)
        
        #mpa is estuary only
        response4 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': self.code4_poly.wkt, 'estuaries': self.ests.wkt})
        self.assertEquals(response4.status_code, 200)
        json4 = serializers.json.simplejson.loads(response4.content)
        self.assertEquals(json4["status_code"], '4')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=self.code4_poly, estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '4')
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToEstuaries/', {})
        self.assertEquals(response6.status_code, 200)
        json6 = serializers.json.simplejson.loads(response6.content)
        self.assertEquals(json6["status_code"], '6')
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator()
        result = estuary_clipper.manipulate()
        self.assertEquals(result["status_code"], '6')
        self.assertEquals(result["clipped_shape"], None)
        self.assertEquals(result["original_shape"], None)
        
    
    #Tests mpa geometries appropriate for the nc_mlpa study region 
    def clipToNCMLPATest(self):
        '''
            Tests the following:
            code_status 0:  clipped to study region
        '''
        study_region = StudyRegion.objects.all()[0].geometry 
        
        w = study_region.extent[0]
        s = study_region.extent[1]
        e = study_region.extent[2]
        n = study_region.extent[3]
        
        center_lat = study_region.centroid.y 
        center_lon = study_region.centroid.x
                
        target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))
        target_shape.set_srid(settings.GEOMETRY_DB_SRID)
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #clip to study region
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': target_shape.wkt})
        self.assertEquals(response0.status_code, 200)
        json0 = serializers.json.simplejson.loads(response0.content)
        self.assertEquals(json0["status_code"], '0')
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=target_shape)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
       
    