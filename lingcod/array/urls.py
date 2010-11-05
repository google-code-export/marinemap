from django.conf.urls.defaults import *
from lingcod.common.utils import get_array_form

urlpatterns = patterns('lingcod.array.views',
    url(r'^(?P<pk>\d+)/add_mpa/$', 'add_mpa', name='array-add-mpa'),
    url(r'^(?P<pk>\d+)/remove_mpa/$', 'remove_mpa', name='array-remove-mpa'),
    url(r'^(?P<pk>\d+)/copy/$', 'copy', name="array-copy"),
    url(r'^(?P<pk>\d+)/download/(?P<filenum>\d+)/$', 'download_supportfile', name="array-download"),
)
