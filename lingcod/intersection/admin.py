from django.contrib.gis import admin
from lingcod.intersection.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf.urls.defaults import patterns, url
from django.forms import TextInput, Textarea

def load_to_features(modeladmin, request, queryset):
    for shp in queryset:
        shp.load_to_features()
    return HttpResponseRedirect('../intersectionfeature')
load_to_features.short_description = 'Load the selected shapefiles to intersection features'

def process_continuous_proxy_line(modeladmin, request, queryset):
    for shp in queryset:
        shp.process_proxy_line()
    return HttpResponseRedirect('../singlefeatureshapefile')

def validate_feature_mapping(modeladmin,request,queryset):
    mismatch_errors = []
    missing_errors = []
    for osc in queryset:
        for fm in osc.featuremapping_set.all():
            if not fm.validate_feature_count(quiet=True):
                error = {}
                error['fieldmap'] = fm.name
                error['scheme'] = osc.name
                error['scheme_pk'] = osc.pk
                missing_errors.append(error)
            elif not fm.validate(quiet=True):
                #error_str = 'There is an output unit mismatch in the \'%s\' fieldmap of the \'%s\' organization scheme.' % (fm.name, osc.name)
                error = {}
                error['fieldmap'] = fm.name
                error['scheme'] = osc.name
                error['scheme_pk'] = osc.pk
                mismatch_errors.append(error)
    return render_to_response('featuremap_validation.html', {'mismatch_errors': mismatch_errors, 'missing_errors': missing_errors,})
validate_feature_mapping.short_description = "Validate Feature Mapping"

        
def create_organization_scheme(modeladmin,request,queryset):
    osc = OrganizationScheme(name='New Scheme')
    osc.save()
    count = 0
    for feature in queryset:
        count += 1
        fm = FeatureMapping()
        fm.organization_scheme = osc
        fm.sort = count
        fm.name = feature.name
        fm.save()
        fm.feature = [feature]
        fm.save()
    ret_path = '../organizationscheme/%s/' % str(osc.pk)
    return HttpResponseRedirect(ret_path)
create_organization_scheme.short_description = 'Create Organization Scheme From Selected Features'

def copy_organization_scheme(modeladmin,request,queryset):
    pks = []
    for orgsc in queryset:
        new = orgsc.copy()
        pks.append(new.pk)
    ret_path = '../organizationscheme/'
    return HttpResponseRedirect(ret_path)
copy_organization_scheme.short_description = 'Copy Organization Scheme'
        
class TestPolygonAdmin(admin.GeoModelAdmin):
    pass

admin.site.register(TestPolygon, TestPolygonAdmin)

class IntersectionFeatureAdmin(admin.ModelAdmin):
    list_display = ('id','name','feature_model','date_created','date_modified')
    list_filter = ['date_modified']
    fieldsets = [
        (None,  {'fields': (('name','description'),('study_region_total','output_units','native_units'),('multi_shapefile','shapefile','feature_model'),)}),
    ]
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'size':'15'})},
            models.TextField: {'widget': Textarea(attrs={'rows':6, 'cols':60})},
        }
    readonly_fields = ('study_region_total',)
    actions = [create_organization_scheme]
admin.site.register(IntersectionFeature, IntersectionFeatureAdmin)

class ShapefileFieldInline(admin.TabularInline):
    model = ShapefileField
    fields = ['name','distinct_values']
#    readonly_fields = ('name','distinct_values',)
#    sort = sort
    extra = 0

class FeatureMappingInline(admin.TabularInline):
    formfield_overrides = {
            models.FloatField: {'widget': TextInput(attrs={'size':'4'})},
            models.CharField: {'widget': TextInput(attrs={'size':'15'})},
            models.TextField: {'widget': Textarea(attrs={'rows':17, 'cols':40})},
        }
    filter_horizontal = ('feature',)
    model = FeatureMapping
    extra = 1
    
class OrganizationSchemeAdmin(admin.ModelAdmin):
    actions = [validate_feature_mapping, copy_organization_scheme]
    inlines = [FeatureMappingInline]

admin.site.register(OrganizationScheme, OrganizationSchemeAdmin)
    
class MultiFeatureShapefileAdmin(admin.ModelAdmin):
    list_display = ('name','date_created','date_modified')
    fieldsets = [
        (None,               {'fields': ('name','shapefile')}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    actions = [process_continuous_proxy_line]
    #inlines = [ShapefileFieldInline]
    
    def get_urls(self):
        from lingcod.intersection.views import split_to_single_shapefiles as splitview
        urls = super(MultiFeatureShapefileAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^splitonfield/(\d+)$', splitview, name='split_to_single_shapefiles')
        )
        return my_urls + urls
    
admin.site.register(MultiFeatureShapefile, MultiFeatureShapefileAdmin)

class SingleFeatureShapefileAdmin(admin.ModelAdmin):
    list_display = ('name','date_created','date_modified')
    actions = [load_to_features]
    fieldsets = [
        (None,               {'fields': (('name','parent_shapefile'),('shapefile','clip_to_study_region'))}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    
admin.site.register(SingleFeatureShapefile, SingleFeatureShapefileAdmin)
#admin.site.register(LinearFeature)
