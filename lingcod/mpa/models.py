from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.common.utils import LookAtKml

from managers import *

class Mpa(models.Model):
    """Model used for representing marine protected areas or MPAs

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Owner of the MPA

        ``name``                Name of the MPA
                                
        ``date_created``        When the MPA was created. Is not changed on
                                updates.
        ``date_modified``       When the MPA geometry was last updated.

        ``editable``            Whether or not the MPA can modified.
        
        ``geometry_orig``       PolygonField representing the MPA boundary as
                                originally drawn by the user
        
        ``geometry_final``      PolygonField representing the MPA boundary
                                after postprocessing.
        ======================  ==============================================
"""   
    user = models.ForeignKey(User)
    name = models.TextField(verbose_name="MPA Name")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    editable = models.NullBooleanField(default=True,null=True, blank=True, editable=False)
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Original MPA boundary")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Final MPA boundary")   
    objects = MpaManager()
    
    class Meta:
        abstract=True
        
        
    def lookAtKml(self):
        """
        Get the kml for a camera perspective looking at the MPA's final geometry
        """
        return LookAtKml( self.geometry_final )
    
    
    def kmlOrigGeom(self, style_domain):
        self.geometry_orig.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' original geometry</name>' + self.kmlOrigGeomStyle(style_domain) + LookAtKml( self.geometry_orig ) + self.geometry_orig.kml + '</Placemark>'
    
    def kmlFinalGeom(self, style_domain):
        self.geometry_final.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' final geometry</name>' + self.kmlFinalGeomStyle(style_domain) + LookAtKml( self.geometry_final ) + self.geometry_final.kml + '</Placemark>'
        
    
    def kmlOrigGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ffffff</color> </PolyStyle></Style>'
    
    
    def kmlFinalGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ff0000</color> </PolyStyle></Style>'
        
        
    def kmlFolder(self, style_domain):
        """
        Return a kml folder containing the kml for this mpa's final and orginal geometry
        """
        return '<Document><name>MPAs</name><Folder>' + '<name>' + self.name + '</name>' + self.kmlFinalGeom(style_domain) + self.kmlOrigGeom(style_domain) + '</Folder></Document>'
        
