# Introduction #

The current MarineMap client uses Google Earth which is fairly resource intensive, requires a plugin that runs only on limited platforms and uses a 3D interface that complicates the traditional 2D layer handling (specifically ordering for display and interaction and dealing with terrain and earth curvature).

The purpose of this page is to investigate the possibility of using a 2D front end such as OpenLayers.

# Pros/Cons of 2D Maps #

## Pros ##

  * 2D maps function more like a stack of data layers do you're not dealing with elevation.  They can be reordered on top of one another, their transparency changed, etc. allowing you to look at multiple layers together in unique ways.

# OpenLayer #

OpenLayers has it's own limitations when dealing with KML data:
  * rendering is extremely slow even with small datasets
  * the full KML spec is not implemented
  * it doesn't respect the regions and network links making loading large datasets extremely problematic.

In short OpenLayer's KML support, while getting better, is nowhere near ready for prime time.

This means we'd need to rely on another representation of MM features; possibly geojson?

## Parts that would need a refactor ##

  * kmlEditor & kmlTree would need to be completely dropped/rewritten to handle the geojson output. We could still leverage workspace docs.
  * Almost all of the javascript which dealt directly with the Google Earth API (a significant portion)
  * kmlapp and all server side code would need to represent features in geojson
  * alternate ways of communicating styling info (css?)
  * alternate ways of simulating networklinks for async loading of data.
  * digitizing and manipulators
  * tools
  * data layers would need to be converted away from KML

## What would it mean to support 2D and 3D maps together ##

  * Would need to simplify data layers to support the vector limitations of client-side Javascript maps
  * -or- would need to support tile-based alternatives for 2D with say WMS feature queries
  * example of what this could look like (GeoCommons): http://geocommons.com/maps/22280.  They are clearly restricting to simpler datasets that are meant to be viewed one at a time.  Things break down likely when you want to view multiple data layers


## Conclusion ##

At this point, I'd be inclined to say that refactoring for 2D maps may be pretty close to a **complete** client-side rewrite plus some substantial server-side refactoring in some apps (kmlapp in particular)

# Google Maps #
Another possibility is to use the Google **Maps** API. Depends on KML support.