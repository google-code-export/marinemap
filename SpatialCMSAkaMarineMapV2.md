# MarineMap 2.0 - The Spatial CMS #

As discussed during our last dev meeting, MarineMap needs an overhaul of the model layer and UI to be more flexible as far as the feature classes it can support, and ease the management of these within the UI.

&lt;wiki:gadget width="410" height="342" url="http://wiki.marinemap.googlecode.com/hg/gadgets/cms.xml" /&gt;

## Objectives ##

  * User-defined content would be represented as Feature classes or FeatureCollection classes rather than repurposing the Mpa and Array classes for everything. In addition, we would be able to support multiple subclasses of these in the same application. Mpas and Arrays will be removed from lingcod.
  * This refactoring would greatly streamline the process of customizing and deploying MarineMap for MSP and other spatial planning projects. In simple cases, a MarineMap project could be customized to support the design of Wind Farms, Folders, Undersea Cables, and Arrays of MPAs by editing one file. [preliminary example](#ExampleModelSyntax.md). We've built up a lot of conventions in deploying MarineMap that are supported by boilerplate code. Lets reduce some of that.
  * Will to some degree formalize MarineMap's interaction design into a framework. Each feature class will have standard editing behavior, information architecture through the sidebar, and there will be an api to extend the export options and outputs related to it.

## Example Model Syntax ##

```
@features.register
class WindFarm(models.FeatureClass):
    """Offshore wind renewable energy site"""
    # inherits user, name, modification date fields
    # user-editable and final clipped component are implied
    geometry = models.UserEditablePolygon(
        srid=settings.GEOMETRY_DB_SRID, 
        manipulators=["lingcod.manipulators.ClipToStudyRegion"])
    bladelength = models.PositiveIntegerField(help_text="fan blade length in meters")
    grid = models.ForeignKey(Grid, blank=False)
    description = models.TextField()
    
    def copy(self, user):
        copy = super(WindFarm, self).copy(*args, **kwargs)
        copy.grid = [] 
        copy.save()
        return copy
    
    class Meta:
        share = True
        form = WindFarmForm
        base_url = "/windfarms/"
        show_template = "windfarms/show.html"
        alternate_links = (
            ('windfarms.views.shapefile', 'Shapefile', 'single'),
            ('windfarms.views.multi_shapefile', 'aggregate Shapefile', 'multiple'),
            ('windfarms.views.kmz', 'as KMZ (Google Earth)', 'both')
        )
        edit_links = (
            ('windfarms.views.copy', 'Copy', 'both'),
            ('windfarms.views.delete_with_grids', 'Delete w/grids', 'both')
        )
        copy_method = 'windfarm.Windfarm.copy'
        parent_class = 'renewableenergy.models.Proposal'
        

class WindFarmForm(forms.FeatureClassForm):
    class Meta(BaseArrayForm.Meta):
        model = WindFarm
        widgets = {
            'description': ShortTextarea(),
        }

```

## Important Features ##
### server side ###

  * We won't cut any corners on the beauty of the API. Everything should at least follow the python style guide (pep 8), and fit well into the conventions of the django model api. There's no need to do this quickly since it will all be in a branch for at least 2 months.
  * Some sort of magic reads the model configuration and sets up links that hook into the [app](http://documentation.marinemap.org/rest.htmlREST) so there isn't a bunch of boilerplate (or worse non-DRY) code that has to go into url files.
  * All configuration can be done from the model. This would include both simple and advanced use cases. Sensible defaults would be provided for many properties. Using this model declaration the following can be specified:
    * geometry type and manipulators
    * attributes to be collected
    * the form class to use for attributes
    * links that should be shown in the toolbar UI - exports and alternate representations, special editing actions, downloadable spreadsheets
    * templates to use for sidebar content and kml representation
    * enable/disable/customize built-in CRUD+copy functionality
    * enable sharing of the shape (would still need to assign permissions via admin)
    * see [Model Definition Details](#ModelDefinitionDetails.md) for more info
  * Feature classes can be points, lines, polygons, or 3d models(essentially points with orientation).
  * FeatureCollection classes can be configured to only support certain Feature and/or FeatureCollection classes as members. Think Arrays of MPAs, and nested Folders.
  * Default kml styles are provided for points, lines, polygons, and 3d models, but are easily overridden via some convention like `templates/model_name/display.kml`.
  * Speaking of conventions for templates, sidebar content should be in `templates/model_name/show.html`. If not provided, a default template should be displayed that essentially says "this app isn't configured yet. Still a template in templates/model\_name/show.html".
  * From the model definition, [all the link tags necessary](http://mm-01.msi.ucsb.edu/~cburt/kmlext/kml_editing_extensions.html#examples) to provide to the client can be generated by calling a function on the model. Say `atom_links()`?

### client side ###

The client will of course support all these Feature and FeatureCollection classes. It will have to be modified to:

  * Support adapting to information provided in the [atom links within layer lists](http://mm-01.msi.ucsb.edu/~cburt/kmlext/kml_editing_extensions.html#examples).
  * Support drag&drop between Features and FeatureCollections.
  * Multiple select, and actions that can operate on multiple selected features, will be added.
  * Digitizing functionality will be extended to support multiple geometry types (point, line, polygon, 3d model)
  * The workflow for managing and editing features will be improved:
    * You will be able to use the toolbar from a feature's sidebar content
    * Edit actions (copy, delete, delete w/Mpas, etc) will be consolidated into an edit dropdown (like export).
    * search will somehow be supported (different issue?)

### Architecture ###
![http://wiki.marinemap.googlecode.com/hg/images/rest_arch.png](http://wiki.marinemap.googlecode.com/hg/images/rest_arch.png)

### Example "Workspace" Document ###

The current marinemap uses atom links to identify some services to use for each feature. In my research I came across AtomPub Workspace documents, that basically identify how collections interact with entries in an atom feed. Looking at my [old specification](http://mm-01.msi.ucsb.edu/~cburt/kmlext/kml_editing_extensions.html) though, it's clear that I needed to describe client behavior that went well beyond what I could do with link `rel` tags, and ended up with a lot of custom attributes. So much so, that sticking with Atom Links seemed pointless.

So, advantages to the document-level json workspace are:

  * Easier to implement a client
  * No need to worry about atom links when templating for individual feature classes
  * Smaller file size (not huge, but still around 10%)
  * Better client performance, since kml documents don't need to be put into a DOM whenever a user interacts with something
  * Better startup performance for kmlEditors

Disadvantages:

  * Not good for SEO (though I'm not sure anyone would spider those links anyhow)
  * Can only specify behavior for all feature-classes, not for individual features (ie you can share this MPA but not this one because it is an SMR).

This document is one level of abstraction deeper than the model definition. The model definition would cover 90% of our use cases, or at least if it didn't we would strive for it to. But when a project implementation needed something particularly custom, there would be an opportunity somewhere in the system to modify the workspace of both MyShapes and ShareShapes (or a new editor) directly. _I'm not sure where that extension point is yet_.

```
{
    feature_classes: [
        {
            id: 'mlpa_mlpampa',
            title: 'Marine Protected Area',
            link_relations: {
                self: {
                    url_template: 'http://northcoast.marinemap.org/mpas/{pk}/'
                },
                create: {
                    title: 'Marine Protected Area'
                    url: 'http://northcoast.marinemap.org/mpas/form/',
                },
                edit: [
                    {
                        title: 'edit',
                        url_template: 'http://northcoast.marinemap.org/mpas/{pk}/form/'
                    },
                    {
                        title: 'copy',
                        // Allow more than one to be copied at a time (pk+)
                        url_template: 'http://northcoast.marinemap.org/mpas/copy/{pk+}/',
                        form: false
                    },
                    {
                        title: 'share',
                        url_template: 'http://northcoast.marinemap.org/sharing/mlpa_mlpampa/{pk}'
                    },
                    // notice no delete, since it's implied by having a self link
                    // here is an example of a project-specific method that would show up in the edit menu
                    {
                        title: 'flag for review',
                        url_template: 'http://northcoast.marinemap.org/flag/{pk}',
                        form: false, // means don't show a form, just POST to url then refresh tree
                        confirm: 'Are you sure you want to flag this item?'
                    }
                ],
                alternate: [ // export menu
                    {
                        title: 'as kmz (Google Earth)',
                        url_template: 'http://northcoast.marinemap.org/kml/e01fb19ec801771605d45d2013d1dad1/{pk+}/mpa.kmz',
                        type: 'application/vnd.google-earth.kmz',
                    },
                    {
                        title: 'as Shapefile',
                        url_template: 'http://northcoast.marinemap.org/mpa/shapefile/{pk+}/',
                        type: 'application/shapefile',
                        multiple: true
                    },
                ]
                // other menus could be added in the future, but there is no 
                // built-in extensibility
            }
        },
        {
            id: 'mlpa_array',
            title: 'Array',
            link_relations: {...},
            collection: {
                // both of these methods would support dragging more than one 
                // feature in or out
                classes: ['mlpa_mpa'], // notice that this could be many types
                remove: {
                    url_template: 'http://northcoast.marinemap.org/collections/mlpa_array/remove/{pk+}'
                },
                add: {
                    url_template: 'http://northcoast.marinemap.org/collections/mlpa_array/add/{pk+}'
                }
            }
        }
    ]
}
```

### documentation ###

  * Docs will have to be tweaked to focus away from MPAs and Arrays.
  * Need pages for:
    * REST/KML Format - for advanced developers only. This drives the framework, but isn't used by framework users.
    * Model API - User Guide and API pages - Maybe need another name for this. Guide for how to use the CMS features of MarineMap


## Development Roadmap ##

We'll need to build this functionality in its own isolated branch since the changes are so far reaching. All of our old projects will need considerable work to get them compatible with 2.0. The branch for this work can be found here:

[2.0-cms branch](http://code.google.com/p/marinemap/source/browse/?r=59c3752145464e3dd6fd24f9a46422689ab491e2)

We'll need to get this branch done before the end of the year, with a little time to apply it to OMM to support folders.

### Tickets ###

### Open Questions ###
#### multiple base classes versus custom geometry fields ####

I (Chad) see two ways of supporting multiple geometry types. One would be to have several base classes (PointFeature, PolygonFeature, etc). The other would be to have a single base class (Feature), and custom field types for geometry:
```
  geometry = models.UserEditablePolygon(
      srid=settings.GEOMETRY_DB_SRID, 
      manipulators=["lingcod.manipulators.ClipToStudyRegion"])
  bladelength = models.PositiveIntegerField(help_text="fan blade length in meters")
```
The fields would actually represent many database attributes (two geometry fields, manipulators used), and sort of wrap the manipulators into form validation for simplicity. This approach would be nice because you could potentially have multiple geometry fields on one feature. Say a wave energy site + energy transmission line. Downside is complexity, this might be overkill. Something to think about.

#### magic ####

_How do we setup urls from the model definitions?_

Maybe the REST app should provide a way to register models. rest.register(WindFarm)? This would be explicit and not require any fancy model introspection. It also would make it easy to register models from other apps. So, this rest.register step would:
  * register any urls specified by `alternate_links`, `edit_links`, etc
  * similarly register any links that are implied, such as the edit, show, delete, type links.
  * maybe do some simple testing to head-off problems?

#### Meta object and inheritance ####

_How do we make sure the model's REST configuration is inherited in subclasses?_

#### KML Generation ####

We've got a whole suite of tools geared towards kml generation for mpas and arrays, and we'll need to extract those and make them available to implement new features. The representation of an individual feature will be different (possibly radically) from feature class to feature class, but the organization of those features is likely to be pretty similar.

We might provide templates for each feature class type (Polygon, Point, Linestring, Model), but then have some easy way of overriding templates using the existing django template overriding methods. These templates would likely _always_ be overridden, but it's nice to have defaults. A second set of templates would deal with structuring a user's shapes, and structuring shared shapes using the same scheme we've used for the MLPA and in Oregon. These would likely be unaltered in most projects, but we would still want to be able to override them.

#### Shape definition on the client side ####

Not sure how to deal with drawing points, lines, and 3d models. the earth-api-utility-library has good means of doing this, but there will need to be some way of invoking these different methods, and thinking about how they do/don't integrate with manipulators.

# Migration of lingcod 1.x apps to lingcod 2.x #

In order to port marinemap instances over to the 2.0 cms branch, the application will need to several changes.

#### Base classes ####
Old MPA/Array-based models will need to inherit instead from PolygonFeature and FeatureCollection classes. In addition they'll need to register with the feature app and explicitly set the Array's collection behavior. For example, in 1.x:

```
class MlpaMpa(Mpa):
    ....

class MpaArray(BaseArray):
    ...
```

would become:

```
@features.register
class MlpaMpa(PolygonFeature):
    ....

@features.register
class MpaArray(FeatureCollection):
    ....
    class Options:
        valid_children = ('nc_mlpa.models.MlpaMpa',)
```

#### Sharing ####
sharing\_enable, sharing disable shortcuts
all utility functions moved to lingcod.sharing.utils