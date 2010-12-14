from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.sharing.managers import ShareableGeoManager
from lingcod.features.forms import FeatureForm
from lingcod.features import FeatureOptions
from lingcod.common.utils import asKml
from lingcod.common.utils import clean_geometry
import re
from django.contrib.contenttypes.models import ContentType

class Feature(models.Model):
    """Model used for representing user-generated features

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Creator

        ``name``                Name of the object
                                
        ``date_created``        When it was created

        ``date_modified``       When it was last updated.
                                        
        ======================  ==============================================
    """   
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name="Name", max_length="255")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    # Expose sharing functionality
    sharing_groups = models.ManyToManyField(Group,editable=False,blank=True,null=True,verbose_name="Share with the following groups")
    
    objects = ShareableGeoManager()

    class Meta:
        abstract=True

    @models.permalink
    def get_absolute_url(self):
        return ('%s_resource' % (self.get_options().slug, ), (), {
            'pk': self.pk
        })
    
    @classmethod
    def get_options(klass):
        return FeatureOptions(klass)
    
    @classmethod
    def model_uid(klass):
        ct = ContentType.objects.get_for_model(klass)
        return "%s_%s" % (ct.app_label, ct.model)
        
    @property
    def uid(self):
        if not self.pk:
            raise Exception(
                'Trying to get uid for feature class that is not yet saved!')
        return "%s_%s" % (self.model_uid(), self.pk, )
    
    def copy(self, user=None):
        """
        Returns a copy of this feature, setting the user to the specified 
        owner. Copies many-to-many relations
        """
        # Took this code almost verbatim from the mpa model code.
        # TODO: Test if this method is robust, and evaluate alternatives like
        # that described in django ticket 4027
        # http://code.djangoproject.com/ticket/4027
        the_feature = self

        # Make an inventory of all many-to-many fields in the original feature
        m2m = {}
        for f in the_feature._meta.many_to_many:
            m2m[f.name] = the_feature.__getattribute__(f.name).all()

        # The black magic voodoo way, 
        # makes a copy but relies on this strange implementation detail of 
        # setting the pk & id to null 
        # An alternate, more explicit way, can be seen at:
        # http://blog.elsdoerfer.name/2008/09/09/making-a-copy-of-a-model-instance
        the_feature.pk = None
        the_feature.id = None
        the_feature.save()

        the_feature.name = the_feature.name + " (copy)"

        # Restore the many-to-many fields
        for fname in m2m.keys():
            for obj in m2m[fname]:
                the_feature.__getattribute__(fname).add(obj)
    
        # Reassign User
        the_feature.user = user
        the_feature.save()
        return the_feature

class SpatialFeature(Feature):
    """
    Abstract Model used for representing user-generated geometry features. 
    Inherits from Feature and adds geometry-related methods/properties
    common to all geometry types.
    """   
    class Meta(Feature.Meta):
        abstract=True

    def save(self, *args, **kwargs):
        self.apply_manipulators()
        if self.geometry_final:
            self.geometry_final = clean_geometry(self.geometry_final)
        super(Feature, self).save(*args, **kwargs) # Call the "real" save() method
    
    @property
    def kml(self):
        return asKml(self.geometry_final.transform(settings.GEOMETRY_CLIENT_SRID, clone=True))

    @property
    def active_manipulators(self):
        """
        This method contains all the logic to determine which manipulators get applied to an MPA

        If self.manipulators doesnt exist or is null or blank, 
           apply the required manipulators (or the NullManipulator if none are required)

        If there is a self.manipulators string and there are optional manipulators contained in it,
           apply the required manipulators PLUS the specified optional manipulators
        """
        active = []
        try:
            manipulator_list = self.manipulators.split(',')
            if len(manipulator_list) == 1 and manipulator_list[0] == '':
                # list is blank
                manipulator_list = []
        except AttributeError:
            print "No manipulators field - need to migrate sublclassed MPA"
            manipulator_list = [] 

        required = self.__class__.Options.manipulators
        try:
            optional = self.__class__.Options.optional_manipulators
        except AttributeError:
            optional = []

        # Always include the required manipulators in the active list
        active.extend(required)

        if len(manipulator_list) < 1:
            if not required or len(required) < 1:
                manipulator_list = ['NullManipulator']
            else:
                return active 

        for manipulator in manipulator_list:
            manipClass = manipulatorsDict.get(manipulator)
            if manipClass and (manipClass in optional or manipClass == NullManipulator):
                active.append(manipClass)

        return active

    def apply_manipulators(self, force=False):
        if force or (self.geometry_orig and not self.geometry_final):
            print "applying manipulators"
            target_shape = self.geometry_orig.transform(settings.GEOMETRY_CLIENT_SRID, clone=True).wkt
            result = False
            for manipulator in self.active_manipulators:
                m = manipulator(target_shape)
                result = m.manipulate()
                target_shape = result['clipped_shape'].wkt
            if not result:
                raise Exception("No result returned - maybe manipulators did not run?")
            geo = result['clipped_shape']
            geo.transform(settings.GEOMETRY_DB_SRID)
            ensure_clean(geo, settings.GEOMETRY_DB_SRID)
            if geo:
                self.geometry_final = geo
            else:
                raise Exception('Could not pre-process geometry')

class PolygonFeature(SpatialFeature):
    """
    Model used for representing user-generated polygon features. 
    """   
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Original Polygon Geometry")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final Polygon Geometry")
    
    @property
    def centroid_kml(self):
        geom = self.geometry_final.point_on_surface.transform(settings.GEOMETRY_CLIENT_SRID, clone=True)
        return geom.kml

    class Meta(Feature.Meta):
        abstract=True

class LineFeature(SpatialFeature):
    """
    Model used for representing user-generated linestring features. 
    """   
    geometry_orig = models.LineStringField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Original LineString Geometry")
    geometry_final = models.LineStringField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final LineString Geometry")

    class Meta(Feature.Meta):
        abstract=True

class PointFeature(SpatialFeature):
    """
    Model used for representing user-generated point features. 
    """   
    geometry_orig = models.PointField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Original Point Geometry")
    geometry_final = models.PointField(srid=settings.GEOMETRY_DB_SRID, 
            null=True, blank=True, verbose_name="Final Point Geometry")
    
    class Meta(Feature.Meta):
        abstract=True
