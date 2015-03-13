# Introduction #

KML, or more accurately applications such as Google Earth which display KML, are not adept at rendering larger datasets. Performance of the client machine can be slow, bandwidth becomes an issue and crashes in the GE application can occur when large data are loaded without first optimizing the display strategy.

# KML Strategies #
First, the general strategy is discussed. Then various implementation alternatives are presented.

## Single KML ##
> Output the entire file as a single KML document. This works well for moderate-sized datasets on fast hardware. But even (1500?) verticies/points can cause noticable slowing or worse on lower-end hardware.

> ### Arc2Earth ###
> allows you to style in ArcMap and export single-KML directly from SDE

> ### ogr2ogr ###
> converts shapefile to kml directly... poor styling and requires conversion of data.


## Raster Superoverlays ##
Generate raster tiles at varying zoom levels and reference them via network links and regionated KMLs(KML heirarchy). This approach can generate HUGE amounts of data is the extent is large and a number of zoomlevels are requirement. Generally useful only for raster data or for huge vector datasets which would not be appropriate to display as vector. By displaying the data as images you loose the ability to do info queries on the feature.

> ### Arc2Earth ###
> generates superoverlays from arcmap-styled sde layer

> ### Gdal2Tiles ###
> chops up an single existing raster image into superoverlays. Requires a huge initial image to get proper resolution at the higher zoom levels.

> ### Tilecache ###
> allows a mapnik-styled shapefile layer to dynamically generate tiles as we fly around. Good for testing. Can also "pre-seed" the cache and generate a superoverlay KML heirachy for it when complete (see kmt-utils/tilecache/README).


## Vector Superoverlays ##
There may be cases where the vector dataset is large but we  want to display it as vector shapes in the interface rather than converting to raster tiles). This approach may need to be customized to optimize for particular qualities of each dataset. For example, in a dataset with 100k features, you could create multiple levels of data and a kml heirachy such that only large features were displayed zoomed out and, as you zoomed in, the smaller features would appear. We could consider creating altered geometries at different zoom levels (ie show simplified geometries only at high zoom levels). For points we could consider clustering.

_Complex vectors are difficult to render using superoverlays when the dataset does not cover the entire extent of the dataset_. Isobaths are a good example of this. http://maps14.msi.ucsb.edu/kml_test/IsobathsSO/geviewer_nl.kml
> When zooming into these tiles, the tiles from the higher scales are still displayed, and scaled up. This results in those tiles creating blurred edges underneath and around the higher resolution tiles.

> ### Custom ###
> No existing tools can optimize vector KMLs in these ways. Through ogr and libkml, we could develop our own if necessary.

# Testing #
As we will be trying numerous KML strategies, there is a need for a consistent, repeatable test of performance in Google Earth. We have added a [KML tour for testing](http://marinemap.googlecode.com/svn/trunk/kml-utils/TestTour.kmz) which we can run with various combinations of datasets loaded to assess graphics performance. Bottlenecks become apparent when the frame freezes and slows.

In order to quantify the performance, we can use [FRAPS](http://www.fraps.com/) (windows only) to measure the frame rate (frames per second or fps) of the google earth tour.

  * Load fraps
  * Open GE and load the tour and appropriate datasets (should see a number in the corner - that current fps)
  * Hit F11 and start the tour simultaneously (f11 starts the fraps recording but also makes it full screen). Hit F11 to stop recording when tour completes
  * look in c:\Fraps\FRAPSLOG.txt and you'll see an entry like:
```
2009-10-23 16:14:24 - googleearth 
Frames: 2163 - Time: 56716ms - Avg: 38.137 - Min: 3 - Max: 61
```

Things to look out for:
  * Compare avg fps between layers - seems to be very repeatable, precise and a good match to the qualitative "feel" of the layer's performance.
  * If time deviates significantly upwards and/or you see min fps of 0, that means rendering was completely stalled for a time. Not good.
  * Make sure other layers and settings are consistent when comparing times (terrain settings and built-in layers can slow things way down)