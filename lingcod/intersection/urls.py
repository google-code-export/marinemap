from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    #(r'multifeatureshapefile/splitbyfield/$',upload_intersection_feature),
    
    (r'^login', 'django.contrib.auth.views.login'),
    (r'^intersect$', intersect ),
    (r'^intersect/testpolygon', test_poly_intersect),
)
