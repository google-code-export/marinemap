#summary Generate static maps for reports using mapnik

Mapnik has been selected as our map rendering engine for static maps:
  * The output is just plain prettier than the alternatives
  * We are using mapnik to generate KML superoverlays so the configuration mapfiles can be re-used
  * Mapnik is arguably easier to install than mapserver
  * The python interface is clean and works very well with django
  * It works well with all the data sources we deal with (shp, postgis)

So the **staticmap** app has been added to lingcod in order to support the generation of static map images generated dynamically by mapnik.

![http://marinemap.googlecode.com/svn/wiki/images/staticmap_default.png](http://marinemap.googlecode.com/svn/wiki/images/staticmap_default.png)

**staticmap** contains a single model, MapConfig, which defines a few basic attributes of the map:
  * the mapnik xml file
  * the default image size
  * the default bounding coordinates
  * ....

Each map has a unique name which can be refered to by URL (eg /staticmap/mymap ). The app ships with a 'default' map which can be accessed at /staticmap or /staticmap/default .

Defaults defined in the model can be overriden by request parameters (eg http://localhost:8000/staticmap/default/?width=1800&height=900&bbox=-120.2,30.2,-116.9,34.5&mpas=2,3,4,5 )

  * width = width of image in pixels
  * height = height of image in pixels
  * bbox = comma-separated list of geographic extents (LL, LR, UL, UR)
  * mpas = comma-separated list of MPA ids
  * array = Array ID (all MPAs associated with this single array will be displayed in addition to the mpas list)

When creating the xml mapfile, do not hardcode the database connection or media path unless you know it will only be deployed on that exact server. Instead, use keywords to be replaced by their corresponding settings:

  * MEDIA\_ROOT - see settings.py
  * GEOMETRY\_DB\_SRID - see settings.py
  * DATABASE\_CONNECTION - takes the place of all postgis Parameter tag set defining postgresql database connections
  * MPA\_FILTER - filter for dynamic MPA lists, use this keyword in the Style > Rule > Filter for MPAs
  * MM\_MPA - the table name for the MPA model

For example, the original mapnik xml for a postgis layer might be:
```
<Style name="mpa_style">
<Rule>
    <PolygonSymbolizer>
        <CssParameter name="fill">rgb(150,0,0)</CssParameter>
    </PolygonSymbolizer>
    <LineSymbolizer>
        <CssParameter name="stroke">rgb(255,255,0)</CssParameter>
        <CssParameter name="stroke-width">0.2</CssParameter>
    </LineSymbolizer>
    <Filter> [id] = 3 or [id] = 4 </Filter>
</Rule>
</Style>

<Layer name="mpa" status="on" srs="+init=epsg:3310">
    <StyleName>mpa_style</StyleName>
    <Datasource>
      <Parameter name="type">postgis</Parameter>
      <Parameter name="table">(select id, geometry, name from simple_app_mpa) as mpa</Parameter>
      <Parameter name="host">localhost</Parameter>
      <Parameter name="dbname">simple</Parameter>
      <Parameter name="user">postgres</Parameter>      
      <Parameter name="password">shhh</Parameter>
    </Datasource>
</Layer>
```
Whereas your xml file for distribution with MarineMap would be:

```

<!-- Don't define mpa_style as this is overridden at runtime -->

<Layer name="mpa" status="on" srs="+init=epsg:GEOMETRY_DB_SRID">
    <StyleName>mpa_style</StyleName>
    <Datasource>
      <Parameter name="type">postgis</Parameter>
      <!-- NOTE: ALL fields below must be included in subselect -->
      <Parameter name="table">(select id, geometry, name, designation_id from MM_MPA) as mpa</Parameter>
      DATABASE_CONNECTION
    </Datasource>
</Layer>
```