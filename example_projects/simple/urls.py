from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'lingcod.common.views.map'),
    (r'^tests/', 'django.views.generic.simple.direct_to_template', {'template': 'common/tests.html'}),
    (r'^panels/$', 'django.views.generic.simple.direct_to_template', {'template': 'common/panel_tests.html'}),
    (r'^layers/', include('lingcod.layers.urls')),

    url(r'^panels/one/', 'django.views.generic.simple.direct_to_template', {'template': 'common/panel_test_one.html'}, name="panel_test"),
    url(r'^panels/one/', 'django.views.generic.simple.direct_to_template', {'template': 'common/panel_test_two.html'}, name="tab_panel_test"),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Useful for serving files when using the django dev server
urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)
