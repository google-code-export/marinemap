from django.conf.urls.defaults import *

urlpatterns = patterns('simple_app.views',
    (r'^sample/manipulator/$', 'sampleManipulator'),
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='mpa-manipulator-list' ),
)