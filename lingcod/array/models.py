from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from lingcod.common.utils import get_mpa_class, get_array_class
from lingcod.array.managers import ArrayManager

class MpaArray(models.Model):
    """
    Represents a grouping or potential network of Marine Protected Areas. Many
    subclasses of lingcod.mpa.models.Mpa (the same subclass) can be associated 
    with an Array. 
    
    Additional information for each MpaArray can be collected by creating a
    subclass of this model.
    
    ======================  ==============================================
    Attribute               Description
    ======================  ==============================================
    ``user``                Owner of the Array

    ``name``                Name of the Array
                            
    ``date_created``        When the Array was created. Is not changed on
                            updates.
    ``date_modified``       When the Array geometry was last updated.
    ======================  ==============================================
    """
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name="Array Name", max_length=255)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    description = models.TextField(blank=True)
    # Expose sharing functionality
    sharing_groups = models.ManyToManyField(Group,editable=False,blank=True,null=True,verbose_name="Share this array with the following groups")
    
    class Meta:
        permissions = (("can_share_arrays", "Can share arrays"),)
        abstract=True
    
    def __unicode__(self):
        return self.name
    
    def add_mpa(self, mpa):
        """Adds a specified Marine Protected Area to the Array"""
        mpa.add_to_array(self)
    
    def remove_mpa(self, mpa):
        """Simply removes an MPA from the Array. The MPA will not be deleted."""
        if mpa.array == self:
            mpa.remove_from_array()
        else:
            raise Exception('MPA `%s` is not in Array `%s`' % (mpa.name, self.name))
        
    @property    
    def mpa_set(self):
        """Returns a queryset of all Marine Protected Areas that are a part of 
        this Array. 
        
        Note: This includes any MPAs that may not be defined by the user, 
        such as existing MPAs that cannot be modified by the user. In the 
        future, these MPAs might be associated with the Array by copies, or by
        reference. This implementation detail is irrelevant for this inteface
        however, as it will always behave the same!
        """
        Mpa = get_mpa_class()
        return Mpa.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk)
    
    @models.permalink
    def get_absolute_url(self):
        return ('array_resource', (), {
            'pk': self.pk
        })
    objects = ArrayManager()

    def copy(self, user):
        """
        Creates a copy of itself, 
        retains many-to-many fields and regular fields but drops sharing reassigns the owner
        Also makes a copy of every mpa in the set and assigns them to this new array
        """
        the_array = self

        # Make an inventory of all mpas belonging to this array
        mpas = the_array.mpa_set

        # Make an inventory of all many-to-many fields in the original mpa
        m2m = {}
        for f in the_array._meta.many_to_many:
            m2m[f.name] = the_array.__getattribute__(f.name).all()

        # The black magic voodoo way, 
        # makes a copy but relies on this strange implementation detail of setting the pk & id to null 
        # An alternate, more explicit way, can be seen at:
        # http://blog.elsdoerfer.name/2008/09/09/making-a-copy-of-a-model-instance
        the_array.pk = None
        the_array.id = None
        the_array.save()

        the_array.name = the_array.name + " (copy)"

        # Restore the many-to-many fields
        for fname in m2m.keys():
            for obj in m2m[fname]:
                the_array.__getattribute__(fname).add(obj)
    
        # Reassign User
        the_array.user = user

        # Copy the individual MPAs and associate them with this new array
        for mpa in mpas:
            new_mpa = mpa.copy(user)
            new_mpa.add_to_array(the_array)

        # Make sure we are not sharing it with anyone
        the_array.sharing_groups.clear()
        
        # The copy of a I-Team proposal doesn't necessarily become a proposal too
        try:
            the_array.proposed = False
        except:
            pass # no proposed field in the inherited array model

        # Save one last time just to be safe?
        the_array.save()
        return the_array
