from django.contrib.gis.utils import LayerMapping
from models import *


def prep_layer_mapping(shpfile_name, model, mapping):
    shpfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', shpfile_name))
    lm = LayerMapping(model, shpfile, mapping, transform=False, encoding='iso-8859-1')
    return lm