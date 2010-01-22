from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group, Permission

def get_shareables():
    """
    Introspects the current project and looks for 
    * a can_share* permission and its associated model name
    * whether those models have a user field (fk to auth Users)
    * whether those models have a sharing_groups ManyToMany field 
    * whether those model managers implement the all_for_user() method (ie the ShareableGeoManager)

    returns dict of models and their associated sharing permission 
     i.e. {'mlpampa': (<MplaMpa model class>, <CanShareMpa permission instance>) }
    """
    perms = Permission.objects.filter(codename__startswith="can_share")
    shareable = {}
    for p in perms:
        model_class = p.content_type.model_class()
        #TODO this checks if field exists but need to do more robust checking on what type of field, where the fk points, etc
        if model_class.__dict__.has_key('sharing_groups') and \
           model_class.__dict__.has_key('user') and \
           model_class.__dict__['user'].__class__.__name__ == 'ReverseSingleRelatedObjectDescriptor' and \
           model_class.__dict__['sharing_groups'].__class__.__name__ == 'ReverseManyRelatedObjectsDescriptor':
            try:
                model_class.objects.shared_with_user
                shareable[p.content_type.model] = (model_class, p)
            except:
                pass
    return shareable

class SharingError(Exception):
    pass

def share_object_with_group(the_object, the_group):
    """
    The entry point for sharing a 'shareable' object with a group
    * Checks that the user has can_share_whatever permissions
    * Checks that the group to be shared with has the can_share_whatever permissions 
    * Sets 'sharing_group' field
    """
    # See if it's shareable and what the appropos permissions are
    shareables = get_shareables()
    try:
        model_class, permission = shareables[the_object.__class__.__name__.lower()]
    except:
        raise SharingError("This object is not shareable")
    perm_label = ".".join([model_class._meta.app_label,permission.codename])

    # Check that the user is of a group which can share 
    if not the_object.user.has_perm(perm_label):
        raise SharingError("You don't have permission to share this type of object") 

    # Check that the group to be shared with has appropos permissions
    try:
        the_group.permissions.get(id=permission.id)
    except:
        raise SharingError("The group you are trying to share with does not have can_share permissions")

    # do it
    the_object.sharing_groups.add(the_group)
    the_object.save()

