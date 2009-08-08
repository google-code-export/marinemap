from django import forms
#from django.contrib.admin.helpers import AdminForm
from lingcod.intersection.models import *

        
class SplitToSingleFeaturesForm(forms.Form):
    def __init__(self, initial_pk, *args, **kwargs):
        super(SplitToSingleFeaturesForm, self).__init__(*args, **kwargs)
        self.fields['mfshp_pk'].initial = initial_pk
        self.fields['shp_field'].choices = [('', '----------')] + [(str(sf.name), sf.name + ' (' + str(sf.distinct_values) + ')') for sf in MultiFeatureShapefile.objects.get(pk=initial_pk).shapefilefield_set.all().order_by('distinct_values')]
    mfshp_pk = forms.IntegerField(widget=forms.HiddenInput)
    shp_field = forms.ChoiceField(label='Shape file field to split on (# of distinct values in field)')

        