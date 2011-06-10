from django.core.management.base import BaseCommand, AppCommand
from django.conf import settings
from optparse import make_option
import os
import glob
from lingcod.layers.models import PrivateKml
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = "Populates the PrivateKml table from the PRIVATE_KML_ROOT contents .. a good starting point"
    args = '[optional group name to share all KMLs with]'

    # Validation is called explicitly each time the server is reloaded.
    requires_model_validation = False

    def handle(self, groupname=None, *args, **options):
        for pkml in PrivateKml.objects.all():
            pkml.delete()

        if groupname:
            g = Group.objects.get(name=groupname)

        if not os.path.exists(settings.PRIVATE_KML_ROOT): 
            raise Exception("Please create or set up a PRIVATE_KML_ROOT directory (currently set to %s" % 
                    settings.PRIVATE_KML_ROOT)
        for d in os.listdir(settings.PRIVATE_KML_ROOT):
            path = os.path.join(settings.PRIVATE_KML_ROOT,d)
            kmls = glob.glob(os.path.join(path,'*.km*'))
            if len(kmls) == 0:
                print "No KML/KMZ found in %s" % path
                continue

            for kml in kmls:
                basename = os.path.basename(kml).split('.')[0]
                pkml = PrivateKml.objects.create(name=d+"_"+basename,base_kml=kml)
                if groupname:
                    pkml.sharing_groups.add(g)
                print "Created %s from %s" % (pkml,kml)
