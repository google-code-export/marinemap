from django.contrib.gis.db import models
from django.conf import settings
from lingcod.common.utils import KmlWrap


class StudyRegion(models.Model):
    """Model used for representing study regions

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Study Region
                                
        ``geometry``            PolygonField representing the study region boundary
        
        ``date_modified``       When the Study Region geometry was last updated.
        
        ``lookAt_Lat``          Latitude of the default look-at point
        
        ``lookAt_Lon``          Longitude of the default look-at point
        
        ``lookAt_Range``        Range camera sits from the default look-at point
        
        ``lookAt_Tilt``         Angle offset from vertical for default camera pos
        
        ``lookAt_Heading``      Angle offset from North for default camera pos
                                
        ======================  ==============================================
"""   
    name = models.TextField(verbose_name="Study Region Name")
    
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Study region boundary")
    
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    
    lookAt_Lat = models.FloatField(default=0, null=True, blank=True)
    lookAt_Lon = models.FloatField(default=0, null=True, blank=True)
    lookAt_Range = models.FloatField(default=80000, help_text='Distance from lookAt point in meters')
    lookAt_Tilt = models.FloatField(default=0, help_text='Degrees from vertical (0=directly above)')
    lookAt_Heading = models.FloatField(default=0, help_text='View direction in degrees (0=look North)')
    
    objects = models.GeoManager()
    
    class Meta:
        db_table = u'mm_study_region'
    
    
    def kml(self):
        transform_geom = self.geometry
        transform_geom.transform(4326)
        retval = '<Placemark> <Style> <LineStyle> <color>ff00ffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>8000ffff</color> </PolyStyle> </Style>' + transform_geom.kml + '</Placemark>'
        return KmlWrap( retval )
    
        
    def lookAtKml(self):
    
        if self.lookAt_Lat == 0.0 and self.lookAt_Lon == 0.0:
            self.computeLookAt()
    
        retval = '<Document><LookAt>\
            <latitude>%f</latitude>\
            <longitude>%f</longitude>\
            <range>%f</range>\
            <tilt>%f</tilt>\
            <heading>%f</heading>\
            <altitudeMode>clampToGround</altitudeMode>\
            </LookAt></Document>' % (self.lookAt_Lat, self.lookAt_Lon, self.lookAt_Range, self.lookAt_Tilt, self.lookAt_Heading )
        return KmlWrap( retval )
        
        
    def computeLookAt(self):
    
        from math import pi, sin, tan, sqrt, pow
        
        DEGREES = pi / 180.0
        EARTH_RADIUS = 6378137.0
  
        trans_geom = self.geometry
    
        w = trans_geom.extent[0]
        s = trans_geom.extent[1]
        e = trans_geom.extent[2]
        n = trans_geom.extent[3]
        
        center_lon = (w + e)/2
        center_lat = (n + s)/2
        
        lngSpan = abs( w - e )
        latSpan = abs( n - s )
        
        aspectRatio = 1.0
    
        PAD_FACTOR = 1.5 # add 50% to the computed range for padding
        
        aspectUse = max( aspectRatio, min((lngSpan / latSpan),1.0))
        alpha = (45.0 / (aspectUse + 0.4) - 2.0) * DEGREES # computed experimentally;
      
        # create LookAt using distance formula
        if lngSpan > latSpan:
            # polygon is wide
            beta = min(DEGREES * 90.0, alpha + lngSpan / 2.0 / EARTH_RADIUS)
        else:
            # polygon is taller
            beta = min(DEGREES * 90.0, alpha + latSpan / 2.0 / EARTH_RADIUS)
      
        self.lookAt_Range = PAD_FACTOR * EARTH_RADIUS * (sin(beta) *
            sqrt(1.0 / pow(tan(alpha),2.0) + 1.0) - 1.0)
            
        trans_geom.transform(4326)
        self.lookAt_Lat = trans_geom.centroid.y
        self.lookAt_Lon = trans_geom.centroid.x
        
        self.lookAt_Tilt = 0
        
        self.save()
    
        
        
        

#    def updated(self):
    
        # expire reports and report caches
        
        # reclip MPA's
        
