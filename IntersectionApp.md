# Introduction #

The basis of habitat reporting in MarineMap is knowing how much habitat is captured within each MPA.  Habitats can be represented as points, lines, or polygons.  These habitat features generally come to us as shapefiles with wildly varying schemas.  The intersection app assists in the process of resolving these various schemas into single feature shapefiles.

Once the habitat features are in simple single feature shapefiles, the intersection app lets you import them in into the database as intersection features.  The features are then available to do intersections with.  However, the more common use case will be to define an organization scheme first.  Organization schemes let you define the order in which feature results are reported and let you combine existing features of the same type (two or more polygon features, for instance) into a single result.

Once the feature data is loaded into the intersection application and the organization scheme is defined, intersection results may be obtained either by directly calling a method of the OrganizationScheme object in the intersection app with a polygon or geometry collection as an arguement or through an http request that includes a polygon in the URL.


---


# Using the Intersection App #


## Getting Intersection Features Into the Intersection App ##

In order to find out how much of a particular feature intersects with a given polygon, we first have to get the intersection feature into the database.  Having each intersection feature represent a single habitat (as opposed to representing different habitats specified by an attribute) provides the greatest flexibility and constancy.   The primary format for habitat data (in our experience so far) are shapefiles.  The schemes of these shapefile data sources vary considerably.

### The Difference Between Multi Feature and Single Feature Shapefiles ###

Sometimes, as is the case with the MLPA linear kelp data sets, the presence of geometry indicates the presence of the habitat.  We'll refer to this type of shapefile as a Single Feature Shapefile.

In other cases, a shapefile may contain geometries that represent any number of different habitats according to how each individual geometry is attributed.  An example of one of these Multi Feature Shapefiles is available [here](http://code.google.com/p/marinemap/source/browse/trunk/lingcod/intersection/test_data/test_substrate.zip).  That example is a portion of the substrate data set used in the South Coast MLPA process.  The shapefile consists of polygons with a sub\_depth attribute (among others).  Some values of this attribute are 'Hard 0 - 30m', 'Soft 30 - 50m', etc.  If we want to know, for instance, how much hard substrate with a depth of 0 - 30 meters is within a given polygon, we want to intersect that polygon with a set of geometries that represent just that habitat type.  In other words, we want to intersect with a single feature rather than a multi feature.

### Turning a Multi Feature Shapefile into Single Feature Shapefiles ###

The intersection app admin can take a zipped multi feature shapefile that has been uploaded and split it into the necessary number of zipped single feature shapefiles.  Once the intersection app is installed and running, you may want to follow these steps in order to acquaint yourself with the app:

  1. Download the [sample substrate shapefile](http://code.google.com/p/marinemap/source/browse/trunk/lingcod/intersection/test_data/test_substrate.zip) to your computer.
  1. Log in to the django admin tool for the intersection app.
  1. Click on 'Multi feature shapefiles' in the intersection admin.
  1. Click the 'Add multi feature shapefile' button on the top right.
  1. Type 'Substrate' into the name field.
  1. Click 'Choose File' and select the sample shapefile (make sure you chose the zipped file) that you downloaded in step 1.
  1. Click the Save button on the bottom right.  You will be taken back to the 'Multi feature shapefiles' list.
  1. Click on the multi feature shapefile you just created (it should be called 'Substrate').
  1. Click on the 'Split to Single Feature Shapefiles' button on the top right.
  1. Chose the shapefile field you want to use to split the multi feature shapefile into single feature shapefiles.
  1. When you click the submit button, you will be taken to the list of single feature shapefiles and you will see that one single feature shapefile has been created for each distinct value in the field that you split on.

### Importing Features from Single Feature Shapefiles ###

Once we have a single feature shapefile, whether it was started life as a single feature shapefile and was imported as such or it started as a multi feature shapefile and was split by the admin tool, we can add it to the Intersection Features model and make it available for intersections.  The following assumes that you've followed the steps above:

  1. Click on "Single feature shapefiles" in the intersection admin.
  1. Select all the substrate shapefiles that were created when you split the multi feature shapefile.
  1. Select "Load the selected shapefiles to intersection features" from the "Action" drop down near the top of the page and click "Go".
  1. This will take you to the list of Intersection Features and you'll see that each of those single feature shapefiles have been imported into the database.


---


## Using Organization Schemes ##

In various parts of your project, you may want to report on intersections differently.  For instance, you may have an array summary page where you want to list results for broad habitat categories while in a more detailed MPA report you may want to show results for more specific categories and you may want to show them in a different order.  Organization schemes give you this flexibility while still caching results at the most detailed level.

### Creating an Organization Scheme ###

Follow these steps to learn about organization schemes by creating one (these steps will assume that you've followed the steps in the previous sections):

  1. Click on "Organization Schemes" in the intersection admin.
  1. Click on "Add organization scheme" in the top right of the screen.
  1. Type "Generalized Substrate" into the name field.
  1. In the "Feature mappings" box type "Hard Substrate" in the name column.
  1. Enter 1 in the sort column.
  1. Select all the features in the feature box that start with "Hard" (Hard 0 - 30m, Hard 30 - 50m, etc.).
  1. Click the "Save and continue editing" button near the bottom right.  A new blank "Feature mapping" row will appear.
  1. Name this one "Soft Substrate and give it an sort value of 2.
  1. Select all the features in the feature box that start with "Soft" (Soft 0 - 30m, Soft 30 - 50m, etc.).
  1. Click the "Save" button.

This "Generalized Substrate" organization scheme can now be used to report on the total hard and soft substrate in an area regardless of depth.

### Using a Shortcut to Create Another Organization Scheme ###

There is a short cut to adding an organization scheme when you want to use most features without aggregation:

  1. Click on "Intersection features" in the intersection app admin.
  1. Check the check boxes next to all of the Hard and Soft features (leave the unknown features unselected).
  1. Choose "Create Organization Scheme From Selected Features" from the Action drop down and click the "Go" button.
  1. Change the name of the organization scheme from "New Scheme" to "Aggregated Unknown".
  1. Alter the sort numbers so that Soft 0 - 30m is first followed by the rest of the Soft categories in order of increasing depth.
  1. Alter the sort numbers for the Hard substrate categories so that they follow the Soft categories in order of increasing depth.
  1. Click the "Save and Continue Editing" button and notice that the field mappings are reordered.
  1. Fill in the final, blank field mapping row with the name "Unknown - all depths" and a sort number of 9.
  1. Select all of the unknown types in the "features" selection box.
  1. Click the "Save" button.

This new organization scheme can be used to report depth stratified results for Soft and Hard substrates but will aggregate results for all unknown substrate, regardless of depth range, into a single result.

### Validating Feature Mapping in an Organization Scheme ###

The intersection app can handle point, line, and polygon features and an organization scheme can handle any combination of these feature types.  However, it does not make any sense at all to aggregate the results from intersection feature of different types.  For instance, if you created a feature mapping that included a linear shoretype feature like beaches (reported in miles) with an areal feature like Soft 0 - 30m substrate (reported in square miles), you would be reporting a unitless and meaningless number.  You can ensure that your organization scheme doesn't include any such bunk feature mappings by following these steps:

  1. Click on "Organization schemes" in the intersection admin.
  1. Check the check box of the Organization scheme you'd like to validate.
  1. Select "Validate Feature Mapping" from the Action drop down and click the "Go" button.
  1. If problems are detected, you'll be presented with links to go fix them otherwise, you'll be congratulated and sent on your way.



---


## Running Test Intersections Within the Intersection App ##

You may want to play around with the intersection app independently of the other apps in your project.  You can do that in a couple of different ways.  You can draw polygons and get results for the intersection features you have loaded into the application.  You can also create test polygons in the admin tool, save them, and get intersection results on them repeatedly.  This helps in evaluating how results are cached.

### Drawing a Polygon and Getting Intersection Results ###

  1. Go to http://YOUR-HOST/intersection/intersect/testdrawing/
  1. Draw a polygon over some portion of the intersection features you've loaded (if you've been following along, that'll be a small portion of the coast just off shore of [Point Conception](http://maps.google.com/maps?f=q&source=s_q&hl=en&geocode=&q=point+conception,+ca&sll=34.42083,-119.69819&sspn=0.31153,0.527344&ie=UTF8&hq=&hnear=Point+Conception,+Lompoc,+Santa+Barbara,+California+93436&t=h&z=10)).
  1. Choose the organization scheme and format for your results.
  1. Click the "Submit" button.