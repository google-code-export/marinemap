from django.contrib.gis import admin
from lingcod.intersection.models import *

def load_to_features(modeladmin, request, queryset):
    for shp in queryset:
        shp.load_to_features()
load_to_features.short_description = 'Load the selected shapefiles to intersection features'

admin.site.register(TestPolygon, admin.GeoModelAdmin)
admin.site.register(IntersectionFeature)

class ShapefileFieldInline(admin.TabularInline):
    model = ShapefileField
    extra = 0

class MultiFeatureShapefileAdmin(admin.ModelAdmin):
    list_display = ('name','date_created','date_modified')
    fieldsets = [
        (None,               {'fields': ('name','shapefile')}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    inlines = [ShapefileFieldInline]
    
admin.site.register(MultiFeatureShapefile, MultiFeatureShapefileAdmin)

class SingleFeatureShapefileAdmin(admin.ModelAdmin):
    list_display = ('name','date_created','date_modified')
    actions = [load_to_features]
    fieldsets = [
        (None,               {'fields': (('name','parent_shapefile'),'shapefile')}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    
admin.site.register(SingleFeatureShapefile, SingleFeatureShapefileAdmin)
#admin.site.register(LinearFeature)