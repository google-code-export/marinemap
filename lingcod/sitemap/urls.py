from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.sitemapviews',
    url(r'^$', 'sitemap', name="sitemap-main"),
)
