from django.contrib import admin
from mlpa.models import *
from lingcod.mpa.admin import MpaAdmin
from lingcod.array.admin import ArrayAdmin

class GoalObjectiveAdmin (admin.ModelAdmin):
    list_display = ( 'goal_category', 'name', 'description')
    list_filter = ['goal_category']
admin.site.register(GoalObjective, GoalObjectiveAdmin)

class GoalCategoryAdmin (admin.ModelAdmin):
    list_display = ('name', 'description')
admin.site.register(GoalCategory, GoalCategoryAdmin)

class AllowedUseAdmin (admin.ModelAdmin):
    list_display = ('target', 'method', 'purpose', 'lop', 'draft', 'rule',)
    list_filter = ['purpose', 'lop', 'draft']
admin.site.register(AllowedUse, AllowedUseAdmin)
admin.site.register(AllowedMethod)
admin.site.register(AllowedPurpose)
admin.site.register(AllowedTarget)
admin.site.register(LopRule)
admin.site.register(DesignationsPurposes)
#admin.site.register(DomainHabitat)
admin.site.register(Lop)

class LopOverrideAdmin(admin.ModelAdmin):
    list_display = ('mpa','pk','lop')
    list_filter = ('lop',)
    search_fields = ('mpa__name','mpa__user__username','mpa__user__first_name','mpa__user__last_name')
    
admin.site.register(LopOverride,LopOverrideAdmin)
# admin.site.register(HabitatsLinear, HabitatsLinearAdmin)
# admin.site.register(HabitatsAreal, HabitatsArealAdmin)
# class SatHabitatAdmin (admin.ModelAdmin):
#     list_display = ('name', 'type', 'sat_standard')
# admin.site.register(SatHabitat, SatHabitatAdmin)
class MpasAdmin (MpaAdmin):
    list_display = ( 'pk', 'name', 'user')
    list_filter = ['user','is_estuary']
admin.site.register(MlpaMpa, MpasAdmin)

from django.contrib.auth.models import Permission
admin.site.register(Permission)

class MpaArrayAdmin(ArrayAdmin):
    list_display = ('name','short_name','user','date_created','date_modified')
    list_filter = ['date_modified','date_created']
    search_fields = ('name','short_name','user__username','user__first_name','user__last_name')
admin.site.register(MpaArray,MpaArrayAdmin)