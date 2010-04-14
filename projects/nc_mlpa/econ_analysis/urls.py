from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'mpa/(\d+)/(\w+)', impact_analysis, name='mpa_impact_analysis'),
    url(r'array/(\d+)/(\w+)', impact_analysis, {'feature': 'array'}, name='array_impact_analysis'),
    #(r'mpa/(\d+)', MpaEconAnalysis), #for testing purposes
    url(r'mpa/print_report/(\d+)/([a-zA-Z\s]+)', print_report, name='mpa_printable_analysis'),
    url(r'array/print_report/(\d+)/([a-zA-Z\s]+)', print_report, {'feature': 'array'}, name='array_printable_analysis'),
)  
