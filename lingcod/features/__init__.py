from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger
from lingcod.common.utils import get_class
from django.template.defaultfilters import slugify
from django.template import loader, TemplateDoesNotExist
from lingcod.features.forms import FeatureForm
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, class_prepared
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from lingcod.sharing.models import ShareableContent
from lingcod.sharing.utils import get_shareables, validate_sharing, sharing_enable, sharing_disable
import json

registered_models = []
registered_links = []
logger = get_logger()

class FeatureConfigurationError(Exception):
    pass

class FeatureOptions:
    """
    Represents properties of Feature Classes derived from both defaults and
    developer-specified options within the Options inner-class. These 
    properties drive the features of the spatial content managment system, 
    such as CRUD operations, copy, sharing, etc.
    
    """
    def __init__(self, model):
        
        # Import down here to avoid circular reference
        from lingcod.features.models import Feature, FeatureCollection    
        
        if not issubclass(model, Feature):
            raise FeatureConfigurationError('Is not a subclass of \
lingcod.features.models.Feature')
        
        self._model = model
        name = model.__name__
        
        if not getattr(model, 'Options', False):
            raise FeatureConfigurationError(
                'Have not defined Options inner-class on registered feature \
class %s' % (name, ))
        
        self._options = model.Options
    
        if not hasattr(self._options, 'form'):
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a form class. \
To specify, add a `form` property to its Options inner-class." % (name,))
        
        if not isinstance(self._options.form, str):
            raise FeatureConfigurationError(
                "Feature class %s is configured with a form property that is \
not a string path." % (name,))
                
        self.form = self._options.form
        """
        Path to FeatureForm used to edit this class.
        """
        
        
        self.slug = slugify(name)
        """
        Name used in the url path to this feature as well as part of 
        the Feature's uid
        """
        
        self.verbose_name = getattr(self._options, 'verbose_name', name)
        """
        Name specified or derived from the feature class name used 
        in the user interface for representing this feature class.
        """
        
        self.form_template = getattr(self._options, 'form_template', 
            'features/form.html')
        """
        Location of the template that should be used to render forms
        when editing or creating new instances of this feature class.
        """
        
        self.form_context = getattr(self._options, 'form_context', {})
        """
        Context to merge with default context items when rendering
        templates to create or modify features of this class.
        """
        
        self.show_context = getattr(self._options, 'show_context', {})
        """
        Context to merge with default context items when rendering
        templates to view information about instances of this feature class.
        """
        
        self.links = []
        """
        Links associated with this class.
        """
        
        opts_links = getattr(self._options, 'links', False)
        if opts_links:
            self.links.extend(opts_links)
        
        self.enable_copy = getattr(self._options, 'disable_copy', True)
        """
        Enable copying features. Uses the feature class' copy() method. 
        Defaults to True.
        """
        
        # Add a copy method unless disabled
        if self.enable_copy:
            self.links.insert(0, edit('Copy', 
                'lingcod.features.views.copy', 
                select='multiple single',
                edits_original=False))
        
        self.valid_children = getattr(self._options, 'valid_children', None)
        """
        valid child classes for the feature container
        """
        if self.valid_children and not issubclass(self._model, FeatureCollection):
            raise FeatureConfigurationError("valid_children Option is only \
                    for FeatureCollection classes" % m)

        self.enable_share = getattr(self._options, 'share', False)
        """
        Enable sharing features. Requires the lingcod.share app.
        """
        if self.enable_share:
            validate_sharing(self._model)

        #TODO test for geom fields and enforce that 
        #  geometry_final is the same type as geometry_original

        self.manipulators = [] 
        """
        Required manipulators applied to user input geometries
        """
        manipulators = getattr(self._options, 'manipulators', []) 
        for m in manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            if geom_field not in manip.Options.supported_geom_fields:
                raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))
            
            logger.debug("Added required manipulator %s" % m)
            self.manipulators.append(manip)
        
        self.optional_manipulators = []
        """
        Optional manipulators that may be applied to user input geometries
        """
        optional_manipulators = getattr(self._options, 'optional_manipulators', [])
        for m in optional_manipulators:
            try:
                manip = get_class(m)
            except:
                raise FeatureConfigurationError("Error trying to import module %s" % m)

            # Test that manipulator is compatible with this Feature Class
            geom_field = self._model.geometry_final._field.__class__.__name__ 
            try:
                if geom_field not in manip.Options.supported_geom_fields:
                    raise FeatureConfigurationError("%s does not support %s geometry types (only %r)" %
                        (m, geom_field, manip.Options.supported_geom_fields))
            except AttributeError:
                raise FeatureConfigurationError("%s is not set up properly; must have "
                        "Options.supported_geom_fields list." % m)
            
            logger.debug("Added optional manipulator %s" % m)
            self.optional_manipulators.append(manip)

        self.enable_kml = True
        """
        Enable kml visualization of features.  Defaults to True.
        """

        # Add a kml link by default
        if self.enable_kml:
            self.links.insert(0,alternate('KML',
                'lingcod.features.views.kml',
                select='multiple single'))

        for link in self.links:
            if self._model not in link.models:
                link.models.append(self._model)
    
    def get_show_template(self):
        """
        Returns the template used to render this Feature Class' attributes
        """
        # Grab a template specified in the Options object, or use the default
        template = getattr(self._options, 'show_template', 
            '%s/show.html' % (self.slug, ))
        try:
            t = loader.get_template(template)
        except TemplateDoesNotExist:
            # If a template has not been created, use a stub that displays
            # some documentation on how to override the default template
            t = loader.get_template('features/show.html')
        return t
    
    def get_valid_children(self):
        if not self.valid_children:
            raise FeatureConfigurationError(
                "%r is not a properly configured FeatureCollection" % (self._model))

        valid_child_classes = []
        for vc in self.valid_children:
            try:
                vc_class = get_class(vc)
            except:
                raise FeatureConfigurationError(
                        "Error trying to import module %s" % vc) 
            
            from lingcod.features.models import Feature
            if not issubclass(vc_class, Feature):
                raise FeatureConfigurationError(
                        "%r is not a Feature; can't be a child" % vc) 

            valid_child_classes.append(vc_class)

        return valid_child_classes

    def get_form_class(self):
        """
        Returns the form class for this Feature Class.
        """
        try:
            klass = get_class(self.form)
        except:
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a valid form class. \
Could not import %s." % (self._model.__name__, self.form))

        if not issubclass(klass, FeatureForm):
            raise FeatureConfigurationError(
                "Feature class %s's form is not a subclass of \
lingcod.features.forms.FeatureForm." % (self._model.__name__, ))

        return klass
    
    def dict(self):
        """
        Returns a json representation of this feature class configuration
        that can be used to specify client behavior
        """
        link_rels = {
            'id': self._model.model_uid(),
            'title': self.verbose_name,
            'link-relations': {
                'self': {
                    'uri-template': reverse("%s_resource" % (self.slug, ), 
                        args=[14]).replace('14', '{id}')
                },
                'create': {
                    'uri-template': reverse("%s_create_form" % (self.slug, ))
                },
                'update': {
                    'uri-template': reverse("%s_update_form" % (self.slug, ), 
                        args=[14]).replace('14', '{id}')
                }
            }
        }
        for link in self.links:
            if not link.generic:
                if link.rel not in link_rels['link-relations'].keys():
                    link_rels['link-relations'][link.rel] = []
                link_rels['link-relations'][link.rel].append(link.dict())
        return link_rels
    
    def json(self):
        return json.dumps(self.dict())
        
    def get_create_form(self):
        """
        Returns the path to a form for creating new instances of this model
        """
        return reverse('%s_create_form' % (self.slug, ))
    
    def get_update_form(self, pk):
        """
        Given a primary key, returns the path to a form for updating a Feature
        Class
        """
        return reverse('%s_update_form' % (self.slug, ), args=[pk])
    
    def get_resource(self, pk):
        """
        Returns the primary url for a feature. This url supports GET, POST, 
        and DELETE operations.
        """
        return reverse('%s_resource' % (self.slug, ), args=[pk])

class Link:
    def __init__(self, rel, title, view, method='GET', select='single', 
        type=None, slug=None, generic=False, models=None, extra_kwargs={}, 
        confirm=False, edits_original=None):
        
        self.rel = rel
        """Type of link - alternate, related, edit, or edit_form.
        """
        
        try:
            self.view = get_class(view)
            """
            View function handling requests to this link.
            """
        except:
            raise FeatureConfigurationError('Link "%s" configured with \
invalid path to view %s' % (title, view))
        
        self.title = title
        """
        Human-readable title for the link to be shown in the user interface.
        """
        
        self.method = method
        """
        For rel=edit links, identifies whether a form should be requested or 
        that url should just be POST'ed to.
        """
        
        self.type = type
        """
        MIME type of this link, useful for alternate links. May in the future
        be used to automatically assign an icon in the dropdown Export menu.
        """
        
        self.slug = slug
        """
        Part of this link's path.
        """
        
        self.select = select
        """
        Determines whether this link accepts requests with single or multiple
        instances of a feature class. Valid values are "single", "multiple",
        "single multiple", and "multiple single". 
        """
        
        self.extra_kwargs = extra_kwargs
        """
        Extra keyword arguments to pass to the view.
        """
        
        self.generic = generic
        """
        Whether this view can be applied to multiple feature classes.
        """
        
        self.models = models
        """
        List of feature classes that a this view can be applied to, if it is 
        generic.
        """
        
        self.confirm = confirm
        """
        Confirmation message to show the user before POSTing to rel=edit link
        """
        
        self.edits_original = edits_original
        """
        Set to false for editing links that create a copy of the original. 
        This will allow users who do not own the instance(s) but can view them
        perform the action.
        """
        
        if self.models is None:
            self.models = []
        
        # Make sure title isn't empty
        if self.title is '':
            raise FeatureConfigurationError('Link title is empty')
        valid_options = ('single', 'multiple', 'single multiple', 
            'multiple single')
        # Check for valid 'select' kwarg
        if self.select not in valid_options:
            raise FeatureConfigurationError(
                'Link specified with invalid select option "%s"' % (
                    self.select, ))
        # Create slug from the title unless a custom slug is specified
        if self.slug is None:
            self.slug = slugify(title)
        # Make sure the view has the right signature
        self._validate_view(self.view)
    
    def _validate_view(self, view):
        """
        Ensures view has a compatible signature to be able to hook into the 
        features app url registration facilities
        
        For single-select views
            must accept a second argument named instance
        For multiple-select views
            must accept a second argument named instances

        Must also ensure that if the extra_kwargs option is specified, the 
        view can handle them
        """
        # Check for instance or instances arguments
        if self.select is 'single':
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instance':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instance.' % (
self.title, ))
        else:
            # select="multiple" or "multiple single" or "single multiple"
            args = view.__code__.co_varnames
            if len(args) < 2 or args[1] != 'instances':
                raise FeatureConfigurationError('Link "%s" not configured \
with a valid view. View must take a second argument named instances.' % (
self.title, ))
            
    @property
    def url_name(self):
        """
        Links are registered with named-urls. This function will return 
        that name so that it can be used in calls to reverse().
        """
        return "%s-%s" % (self.parent_slug, self.slug)
    
    @property
    def parent_slug(self):
        """
        Returns either the slug of the only model this view applies to, or 
        'generic'
        """
        if len(self.models) == 1:
            return self.models[0].get_options().slug
        else:
            return 'generic-links'
        
        
    def reverse(self, instances):
        """Can be used to get the url for this link. 
        
        In the case of select=single links, just pass in a single instance. In
        the case of select=multiple links, pass in an array.
        """
        if not isinstance(instances,tuple) and not isinstance(instances,list):
            instances = [instances]
        ids = ','.join([instance.uid for instance in instances])
        return reverse(self.url_name, kwargs={'ids': ids})
    
    def __str__(self):
        return self.title
    
    def __unicode__(self):
        return str(self)
    
    def dict(self):
        d = {
            'rel': self.rel,
            'title': self.title,
            'select': self.select,
            'uri-template': reverse(self.url_name, 
                kwargs={'ids': 'idplaceholder'}).replace(
                    'idplaceholder', '{id+}')
        }
        if self.rel == 'edit':
            d['method'] = self.method
        if len(self.models) > 1:
            d['models'] = [m.model_uid() for m in self.models]
        return d
    
    def json(self):
        return json.dumps(self.dict())
        
        
def create_link(rel, *args, **kwargs):
    nargs = [rel]
    nargs.extend(args)
    link = Link(*nargs, **kwargs)
    must_match = ('rel', 'title', 'view', 'extra_kwargs', 'method', 'slug', 
        'select')
    for registered_link in registered_links:
        matches = True
        for key in must_match:
            if getattr(link, key) != getattr(registered_link, key):
                matches = False
                break
        if matches:
            registered_link.generic = True
            return registered_link
    registered_links.append(link)
    return link

def alternate(*args, **kwargs):
    return create_link('alternate', *args, **kwargs)

def related(*args, **kwargs):
    return create_link('related', *args, **kwargs)

def edit(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'POST'
    return create_link('edit', *args, **kwargs)

def edit_form(*args, **kwargs):
    if 'method' not in kwargs.keys():
        kwargs['method'] = 'GET'
    return create_link('edit', *args, **kwargs)


def register(model):
    options = model.get_options()
    logger.debug('registering Feature %s' % (model.__name__,) )
    if model not in registered_models:
        registered_models.append(model)
        try:
            if options.enable_share:
                sharing_enable(model)
            else:
                sharing_disable(model)
        except ContentType.DoesNotExist:
            pass # wait until ContentType is created and post_save handler will kick in
        for link in options.links:
            if link not in registered_links:
                registered_links.append(link)
    return model
            
def workspace_json(*args):
    workspace = {
        'feature-classes': [],
        'generic-links': []
    }
    for model in args:
        workspace['feature-classes'].append(model.get_options().dict())
    for link in registered_links:
        # See if the generic links are relavent to this list
        if link.generic and [i for i in args if i in link.models]:
            workspace['generic-links'].append(link.dict())
    return json.dumps(workspace, indent=2)

@receiver(post_save, sender=ContentType)
def contentype_sharing_handler(sender, instance, created, **kwargs):
    """Because sharing involves setting up Permissions and ShareableContent
    which reference the ContentTypes table, we have to wait until the 
    ContentType is created (post_save signal) before we populate those tables. 
    """
    mc = instance.model_class()
    if created and mc in registered_models: # it's a feature
        logger.debug("Feature %r added to contenttypes" % instance)
        if mc.get_options().enable_share: # it's a shareable feature
            sharing_enable(mc)
        else:
            sharing_disable(mc)

#@receiver(class_prepared)
#def class_prepared_handler(sender,**kwargs):
#    print '%r prepared' % sender


