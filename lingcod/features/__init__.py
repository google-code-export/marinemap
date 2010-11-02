from django.conf.urls.defaults import *
from lingcod.common.utils import get_logger
from lingcod.common.utils import get_class
from django.template.defaultfilters import slugify
from django.template import loader, TemplateDoesNotExist
from lingcod.features.forms import FeatureForm
from django.core.urlresolvers import reverse


logger = get_logger()

class FeatureConfigurationError(Exception):
    pass

class FeatureConfig:
    """Represents properties of Feature Classes derived from both defaults and
    developer-specified options within the Config inner-class. These 
    properties drive the features of the spatial content managment system, 
    such as CRUD operations, copy, sharing, etc.
    """
    def __init__(self, model):
        
        # Import down here to avoid circular reference
        from lingcod.features.models import Feature        
        
        if not issubclass(model, Feature):
            raise FeatureConfigurationError('Is not a subclass of \
lingcod.features.models.Feature')
        
        self._model = model
        name = model.__name__
        
        if not getattr(model, 'Config', False):
            raise FeatureConfigurationError(
                'Have not defined Config inner-class on registered feature \
class %s' % (name, ))
        
        self._config = model.Config
    
        if not hasattr(self._config, 'form'):
            raise FeatureConfigurationError(
                "Feature class %s is not configured with a form class. \
To specify, add a `form` property to its Config inner-class." % (name,))
    
        if not isinstance(self._config.form, str):
            raise FeatureConfigurationError(
                "Feature class %s is configured with a form property that is \
not a string path." % (name,))
                
        self.form = self._config.form
        self.slug = slugify(name)
        self.verbose_name = getattr(self._config, 'verbose_name', name)
        self.form_template = getattr(self._config, 'form_template', 
            'rest/form.html')
        self.form_context = getattr(self._config, 'form_context', {})
        self.show_context = getattr(self._config, 'show_context', {})
    
    def get_show_template(self):
        """If the user has specified a show_template, grab that template.
        Otherwise use the convention '{{model_slug}}/show.html. If a template
        doesn't exist at either of those paths, returns the 'rest/show.html'
        template.
        """
        template = getattr(self._config, 'show_template', 
            '%s/show.html' % (self.slug, ))
        try:
            t = loader.get_template(template)
        except TemplateDoesNotExist:
            t = loader.get_template('rest/show.html')
        return t
    
    def get_form_class(self):
        """Return the form class specified in the model configuration."""
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
    
    def json(self):
        """Returns a json representation of this feature class configuration
        that can be used to specify client behavior
        """
        pass
        
    def get_create_form(self):
        return reverse('%s_create_form' % (self.slug, ))
    
    def get_update_form(self, pk):
        return reverse('%s_update_form' % (self.slug, ), args=[pk])
    
    def get_resource(self, pk):
        return reverse('%s_resource' % (self.slug, ), args=[pk])

registered_models = []

def register(*args):
    for model in args:
        model.get_config()
        logger.debug('registering %s' % (model.__name__,) )
        if model not in registered_models:
            registered_models.append(model)