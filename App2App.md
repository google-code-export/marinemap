# Introduction #

The Consortium is in the process of developing multiple MarineMap implementations, or **projects** in contiguous regions along the west coast and will likely be doing the same in other parts of the country. These stand-alone projects allow us to customize MarineMap to meet the needs of specific regional planning projects. While developing purpose-built implementations of MarineMap makes sense to support varying process needs in particular regions, it shouldn't become a barrier to more comprehensive planning. For example, users of the MarineMap Oregon tool should be able to view data layers and MPA proposals developed below their southern border using the MLPA North Coast version of MarineMap.

As these **projects** are hosted in different systems on different domains, data sharing among them is not currently possible. The App2App Communication feature is designed to address that.

## Features and Requirements ##

  * Users of one instance of MarineMap should be able to pan around the globe and discover data exposed by other instances of MarineMap through both the data layers list and "signpost layers" on the map.
  * Users should be able to control the layer display (toggle, expand folders, etc) for these discovered layers in the data layers list.
  * Stakeholder developed spatial designs identified to be shared with the public should be available through this same layers interface. In practice, this means the kml for "Public Proposals" from the MLPA and Public AOIs from Oregon should be accessible.
  * Users should be able to view the attributes of spatial designs by clicking on a ![http://mm-01.msi.ucsb.edu/~cburt/graphics/view_attributes.png](http://mm-01.msi.ucsb.edu/~cburt/graphics/view_attributes.png) button in the shape's popup.
  * All reports should be functional.
  * Individual MarineMap projects can customize what information is exposed via this function. For example, an instance of MarineMap might by default include the public layers list and public spatial designs, but could be customized to show other content like a list of survey sites in the case of [pyrifera](http://code.google.com/p/pyrifera).

## Limitations ##

  * Users will not be able to create or copy spatial designs from one instance of MarineMap to another. Instead, if users wish to participate in a planning process in another region they will need to follow a link to the MarineMap instance hosting that planning process. To make this transition as seamless as possible, the user's selected layers and map location will be transfered to the hosting instance automatically.

## Basic User Interaction ##

![http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-A.png](http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-A.png)

![http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-B.png](http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-B.png)

![http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-C.png](http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-C.png)

![http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-D.png](http://commondatastorage.googleapis.com/mm-wiki/App2AppUX-D.png)


## Technical Notes ##

[Work List](http://code.google.com/p/marinemap/issues/list?q=label:Category-App2App)

  * Content will be loaded across domains
    * KML document that NetworkLinks to all (conforming) MarineMap instances' public layer list and spatial design list will be hosted outside of any particular MarineMap instance.
    * Sidebar content will be loaded via a crossdomain ajax request, or json-p.
  * Shared sidebar content is tricky, because different instances of MarineMap might not have the same stylesheets, javascript, etc. There will need to be some versioning scheme and formalization of how project-specific javascript and css is handled for sidebar content.

## General Architecture ##

![http://commondatastorage.googleapis.com/mm-wiki/app2app-arch.png](http://commondatastorage.googleapis.com/mm-wiki/app2app-arch.png)