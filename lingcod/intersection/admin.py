from django.contrib.gis import admin
from lingcod.intersection.models import *

def load_to_features(modeladmin, request, queryset):
    for shp in queryset:
        shp.load_to_features()
load_to_features.short_description = 'Load the selected shapefiles to intersection features'

class TestPolygonAdmin(admin.GeoModelAdmin):
    pass

admin.site.register(TestPolygon, TestPolygonAdmin)

class IntersectionFeatureAdmin(admin.ModelAdmin):
    list_display = ('id','name','feature_model','date_created','date_modified')
admin.site.register(IntersectionFeature, IntersectionFeatureAdmin)

class ShapefileFieldInline(admin.TabularInline):
    model = ShapefileField
    extra = 0

class FeatureMappingInline(admin.TabularInline):
    model = FeatureMapping
    extra = 1
    
class OrganizationSchemeAdmin(admin.ModelAdmin):
    inlines = [FeatureMappingInline]

admin.site.register(OrganizationScheme, OrganizationSchemeAdmin)
    
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