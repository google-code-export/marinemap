# What's new? #

MarineMap 3.0 built off a proven tool for marine spatial planning and expands it to a tremendously flexible framework for developing web-based spatial decision tools in any domain.

MM3 represents a major overhaul of the lingcod code base. Based on Chad Burt's inital idea of a MarineMap [Content Management System](http://code.google.com/p/marinemap/w/edit/SpatialCMSAkaMarineMapV2), the code was refactored to support not only MPAs and Arrays but any sort of _Features_ or _Feature Collections_ that the project might require. This allows for multiple types of features (e.g. wind farms, MPAs and fishing grounds), point, line and polygon features, and the ability to organize them into collections in any configuration.

These enhancements were made possible by significant changes to the code base. The `lingcod.rest`, `lingcod.sharing`, `lingcod.mpa` and `lingcod.array` modules have been removed; that functionality is encapsulated entirely in the new `lingcod.features` module. The new API means that porting apps from MM2 to MM3 will require some tweaks to your code (see below for details).

MM3, via the `lingcod.features` module, provides a greatly simplified set of tools for rapidly developing custom MarineMap instances. Virtually all of the feature configuration takes place in the model and form definitions. Simply register the feature and the urls, standard views, rest API, sharing configuration and user interface elements are all configured automatically. This allows you to focus on customizing the behavior of your feature to fit the project requirements rather than messing with lower-level scaffolding code.


# Details on Porting MM2 to MM3 #

Information about upcoming changes, and how those changes may impact project implementations.

  * lingcod.common.urls can be imported to handle all built-in django functionality rather than re-implementing urls for each project. Simply include a line like so at the end of a project's urls.py:
```
urlpatterns += patterns('',
    # Include all lingcod app urls. Any urls above will overwrite the common 
    # urls below
    (r'', include('lingcod.common.urls')),
)
```
  * lingcod.common.default\_settings now contains a `DATABASES` setting, matching the new Django 1.2 convention and dropping the now deprecated `DATABASE_*` settings. Remove all `DATABASE_*` settings from project implementations, and override defaults like so:
```
DATABASES['default']['name'] = 'marinemap_project_db_name'
```