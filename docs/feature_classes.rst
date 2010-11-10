The Features App
################

The ``lingcod.features`` app works along with other MarineMap apps to create a 
system that is best described as a content management system for user-designed
spatial features. This system can be configured quickly to support a range of 
management options such as marine protected areas, hydrokinetic generators, 
wind turbines, or undersea cables. With one model definition it's possible to
define the data schema for storing these features, as well as what behaviors 
and actions they support within the MarineMap interface. I high degree of 
customization can be achieved with a MarineMap project with this declarative 
format, without having to customize the view or client-side javascript 
components.

Feature Classes can be configured to:

  * Represent various management scenarios as Point, LineString or Polygon 
    data
  * Collect attributes from users using forms generated from the model 
    definition (or customized forms)
  * Pre-process and validate user-defined geometries with Manipulators
  * Enable sharing of features among users
  * Add custom downloads, like Shapefile or Excel files
  * Support custom editing actions
  
In addition, FeatureCollection Classes can be created that are collections of
Feature Class instances with their own attributes. These can be used to 
represent simple Folders to help users organize their designs, or represent 
management concepts such as Marine Protected Area Networks.

Creating a Spatial Feature Class
********************************

Lets walk through the basics of creating a simple Feature Class. The basic 
process involves:

  * Defining a subclass of ``PointFeature``, ``LineStringFeature``, 
    ``PolygonFeature``, or ``3dModelFeature``, including the attributes to be
    stored with it.
  * Creating an Options inner-class, and using it to specify a form to use 
    when creating or editing this Feature Class.
  * Specifying links to downloads or services related to the Feature Class.
  * Specifying any optional parameters on the Options inner-class
  * Creating a template to use when displaying this Feature Class' attributes
  * Creating a kml template that can be used to represent it
  
Look at this crap example::

    @features.register
    class Mpa(PolygonFeature):
        ext = models.CharField(max_length="12")

        class Options:
            verbose_name = 'Marine Protected Area'
            form = 'myproject.forms.MpaForm'
            links = (
                alternate('Shapefile',
                    'mlpa.views.shapefile', 
                    select='single', 
                    type='application/shapefile'),

                alternate('KMZ (Google Earth)', 
                    'mlpa.views.kml_export', 
                    select='single multiple', 
                    type='application/vnd.google-earth.kmz',
                    generic=True),

                related('MPA Spreadsheet',
                    'mlpa.views.spreadsheet', 
                    select='single',
                    type='application/excel'),

                edit('Delete w/Grids', 
                    'mlpa.views.delete_w_grids', 
                    confirm="Are you sure you want to delete with grids?", 
                    select="single multiple",
                    args=[MpaArray],
                    kwargs={'keyword_argument': True}),

                edit_form('Tags',
                    'mlpa.views.tag', 
                    select='single multiple',
                    generic=True,
                    models=(MpaArray, MlpaMpa)),
            )

Defining the Model
==================

Must be a subclass of one of the ``Feature`` subclasses (``PointFeature``, 
``PolygonFeature``, ``LineStringFeature``, ``3dModelFeature``)

Specifying a Form
=================

All Feature Classes must have an ``Options`` inner-class that contains a 
property specifying the ``FeatureForm`` subclass that can be used to edit it.
All :ref:`other properties <optional-properties>` on the Options inner-class 
are optional.

Creating a "Show" Template
==========================

The show template is used to render sidebar content for a feature within the
MarineMap interface, and can also be used to render a printable and 
bookmarkable page for it. This template can be placed in any template 
directory by default under ``{{slug}}/show.html``. Subdirectories are used to
allow for overriding templates as mentioned in the 
`django documentation <http://docs.djangoproject.com/en/1.2/ref/templates/api/#using-subdirectories>`_.
The default path to the show template can be changed using an optional 
`show_template`_ parameter to the Options inner-class.

Templates will be rendered with the following context:
    
    * ``instance`` - the feature class instance being being displayed
    * ...
    * ...

You can add to this list using the `show_context`_ Option property.

Creating a KML Template
=======================

Create a template under ``{{slug}}/feature.kml`` that represents your feature,
otherwise a default rendering will be used. The tag used must be a 
`KML Feature <http://code.google.com/apis/kml/documentation/kmlreference.html#feature>`_,
and have an ``id`` attribute populated with the value of ``instance.uid``.

KML templates are rendered with the same context as show templates.

Beyond the Basics
=================

Enabling Sharing
----------------

Implementing a Custom Copy Method
---------------------------------

Specifying Manipulators
-----------------------

Etc
---

Base Classes
************

Spatial Types
=============

PointFeature
------------

LineStringFeature
-----------------

PolygonFeature
--------------

3dModelFeature
--------------
Subclass of PointFeature, but with orientation and a 3d model representing it.

FeatureCollection Base Class
============================
Subclasses of FeatureCollection have a one-to-many relationship with one or 
more Feature Classes. One could create a Marine Protected Area Network class 
that can only contain MPAs, or a Folder class that can contain any combination
of FeatureClasses or even other Folders and FeatureCollections.

.. code-block:: python

    class Folder(FeatureCollection):
        class Options:
            # default options, can contain anything
            pass

    class MPANetwork(FeatureCollection):
        class Options:
            child_classes = ('mlpa.models.Mpa', )


The Options inner-class
***********************


.. py:attribute:: form (required)

    Specifies a `ModelForm <http://docs.djangoproject.com/en/dev/topics/forms/modelforms/>`_
    that will be used to create and edit features of this class. The form 
    must be a subclass of lingcod.features.forms.FeatureForm, and the path
    to the form must be provided as a *string*. Otherwise you'll cause 
    circular reference issues.

.. py:attribute:: verbose_name

    Provide your feature class with a human readable name to be used 
    within the interface. For example, this name determines the name used 
    in the "Create" menu. If not specified, the CamelCase model name will 
    be used. Even though it is optional, this property is obviously highly 
    recommended.

.. py:attribute:: show_template

    By default, will look for the template at ``{{modelname}}/show.html`` 
    when rendering shape attributes. For example, the template for a model 
    named MpaArray  would be ``mpaarray/show.html``. You can specify a 
    different template location with this option.

.. py:attribute:: form_template

    Use this option to specify a custom template to be shown when creating
    or editing a feature. By default, looks for a template under 
    ``features/form.html``.

.. py:attribute:: form_context

    Specify a base context to use for rendering templates when creating and 
    editing features.

.. py:attribute:: show_context

    Specify a base context to use when rendering feature attributes.

.. py:attribute:: shareable

    Enabled by default, set to False to disable sharing functionality.

.. py:attribute:: copy

    Enabled by default, set to False to disable copy functionality. Calls the
    copy method of Feature, which can be overriden by subclasses to customize
    this functionality.

.. py:attribute:: manipulators

    fucking manipulators, 
    `how do they work? <http://www.youtube.com/watch?v=_-agl0pOQfs>`_
    Defaults to clipping features to the study region. Set to ``None`` to 
    disable.

.. py:attribute:: kml_template

    Specify a template to use. Defaults to ``{{slug}}/feature.kml``.

.. py:attribute:: links

    Specify links associated a Feature Class that point to related downloads, 
    export tools, and editing actions that can be performed.

Specifying Links
================

Links allow developers to extend the functionality of features by specifying
downloads, actions, or related pages that should be made available through the
interface. There are 4 types of Links:

  * ``alternate`` links specify alternative representations of features that 
    should be made available through the Export menu.
  * ``related`` links specify related downloads or pages that are also made 
    available in the Export menu but in a downloads section.
  * ``edit`` links specify items that should appear in the Edit menu and 
    modify a selected feature, create a copy, or some other 
    `non-idempotent <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_
    action.

Here's an example of links in use::
    
    @register
    class RenewableEnergySite(Feature):
        type = models.CharField(max_length=1, choices=TYPE_CHOICES)
        class Options:
            verbose_name = 'Renewable Energy Site'
            form = 'lingcod.features.tests.RenewableEnergySiteForm'
            links = (
                alternate('Export KML',
                    'lingcod.features.tests.kml',
                    select='multiple single'
                ),
                related('Viewshed Map',
                    'lingcod.features.tests.viewshed_map',
                    select='single',
                    type='image/png'
                ),
                edit('Delete w/related cables',
                    'lingcod.features.tests.delete_w_cables',
                    select='single multiple',
                    confirm="""
                    Are you sure you want to delete this site and associated 
                    undersea cables? 
                    This action cannot be undone.
                    """
                )
            )

creating compatible views
-------------------------

Views that are wired up to features using links must accept a second argument
named ``instance`` or ``instances`` depending on whether they can work on 
single or multiple selected features. 

The features app will handle requests 

Generic views will handle cases where a user is not authorized to view or edit
a feature, requests related to features that cannot be found, and improperly 
configured views. 


link properties
---------------

.. autoclass:: lingcod.features.Link
    :members:
    :no-undoc-members:
    :exclude-members: __init__, url_name, parent_slug, reverse, json