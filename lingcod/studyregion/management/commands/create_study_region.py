from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from lingcod.studyregion.models import StudyRegion

class Command(BaseCommand):
    option_list = AppCommand.option_list + (
        make_option('--name', action='store', dest='region_name', default=False,
            help='Give a name to the study region, otherwise the name attribute from the shapefile will be used.'),
    )
    help = "Creates a new study region from a shapefile containing a single multigeometry"
    args = '[shapefile]'
    
    def handle(self, shapefile, *args, **options):
        ds = DataSource(shapefile)
        if len(ds) != 1:
            raise Exception("Data source should only contain a single layer. Aborting.")

        layer = ds[0]
        if len(layer) != 1: 
            raise Exception("Layer should containing ONLY a single feature")

        if not 'polygon' in layer.geom_type.name.lower():
            print layer.geom_type.name
            raise Exception("Study region must be a multigeometry")

        if options.get('region_name'):
            mapping = {
                'geometry': 'MULTIPOLYGON',
            }
        else:
            mapping = {
                'geometry': 'MULTIPOLYGON',
                'name': 'name',
            }

        lm = LayerMapping(StudyRegion, shapefile, mapping, transform=False)
        lm.save()
        study_region = StudyRegion.objects.order_by('-creation_date')[0]
        if options.get('region_name'):
            study_region.name = options.get('region_name')
            study_region.save()
        print ""
        print "Study region created: %s, primary key = %s" % (study_region.name, study_region.pk)
        
        print "To switch to this study region, you will need to run 'python manage.py change_study_region %s'" % (study_region.pk, )
        print ""
