from django.contrib.gis.db import models
from django.conf import settings
from lingcod.features.models import Feature, FeatureForm
from lingcod.common.utils import get_class
from lingcod.features import register
from django.contrib.gis.geos import GEOSGeometry 
from lingcod.common.utils import asKml
import os

class Analysis(Feature):
    """
    Abstract Feature model representing the inputs and outputs
    of an analysis or modeling run 
    """

    @property
    def kml(self):
        # Note: if you want network links, return None here and
        # use kml_full instead (kml_done wrapped in a full kml Document)
        if self.done:
            return self.kml_done
        else:
            return self.kml_working

    @property
    def kml_done(self):
        """
        Translate the model outputs to KML Placemark or Folder
        """
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s</name>
        </Placemark>
        """ % (self.uid, self.name)

    @property
    def kml_working(self):
        """
        Translate the model outputs to KML Placemark or Folder
        """
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s (Working...)</name>
        </Placemark>
        """ % (self.uid, self.name)

    @property
    def kml_style(self):
        return ""

    @classmethod
    def input_fields(klass):
        return [f for f in klass._meta.fields if f.attname.startswith('input_')]

    @classmethod
    def input_manytomany_fields(klass):
        return [f for f in klass._meta.many_to_many if f.attname.startswith('input_')]

    @property
    def inputs(self):
        """
        Returns a dict of all input parameters
        """
        odict = {}
        for f in self.input_fields():
            odict[f.verbose_name] = self._get_FIELD_display(f)
        return odict

    @classmethod
    def output_fields(klass):
        return [f for f in klass._meta.fields if f.attname.startswith('output_')]

    @property
    def outputs(self):
        """
        Returns a dict of all output parameters
        If processing is incomplete, values will be None
        """
        odict = {}
        for f in self.output_fields():
            odict[f.verbose_name] = self._get_FIELD_display(f)
        return odict

    @property
    def status_html(self):
        if self.done:
            return "<p>All done</p>"
        else:
            return "<p>Not done yet; output fields are still blank"

    @property
    def progress(self):
        """
        How many sub-tasks completed out of a total
        e.g. (3,6) means 3 out of 6 pieces are complete so progress bar can show 50%
        """
        return (1,1)

    @property
    def done(self):
        """
        If it's asynchronously processed, this is the definitive
        property to determine if processing is completed.
        """
        # For now just check that the outputs are not None
        for of in self.outputs.keys():
            if self.outputs[of] is None:
                return False
        return True

    def run(self):
        """
        Method to execute the model. 
        Passes all input parameters to the analysis backend, 
        takes the results and stores in the model output fields. 
        """
        pass

    def clear_output_fields(self):
        """
        Reset button; Sets all output fields to None
        """
        for f in self.output_fields():
            self.__dict__[f.attname] = None

    '''
    Note on keyword args rerun and form: these are extracted from kwargs so that they will not cause an unexpected 
    keyword argument error during call to super.save
    Note on rerun:  When set to false no output fields will be cleared and the run method will not be called
    Note on form:  This is passed from feature.views update and create methods.  In the case of m2m fields this needs to 
    be called after super.save.  Since it also needs to be called before self.run, it needs to be called here in this 
    save method rather than its previous location in feature views update and create (after save has completed)
    '''
    def save(self, rerun=True, *args, **kwargs):
        if rerun:
            self.clear_output_fields() # get rid of old outputs
            super(Analysis, self).save(*args, **kwargs) # have to save first so it has a pk
            self.run()
            super(Analysis, self).save(*args, **kwargs) 
        else:
            super(Analysis, self).save(*args, **kwargs) # have to save first so it has a pk


    class Meta:
        abstract = True
