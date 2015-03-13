# Introduction #

Users need the ability to share map views with each other, both via traditional means such as email, IM, etc and through their user groups within MarineMap. A map view consists of the viewport (map location, zoom level, camera angle), and the state of any data layers. Feature class-based data layers pose a greater challenge than other layers since the organization of MyShapes and SharedShapes will differ across users. An additional challenge is that this functionality should ideally be extended to non-authenticated users, since bookmarking is not a task that typically requires a login.

# UI Design #

## Initiating Bookmark Creation ##

For authenticated users who want to create a bookmark to share among their groups, there ought to be a menu item in the "Create New" menu. This will be simple to implement via MM3.0 Feature Classes. But if bookmarks are to function as both content within a user's MyShapes/Features listing as well as a copy-able url string for unathenticated users, it makes sense to have an additional affordance.

Option A

![http://wiki.marinemap.googlecode.com/hg/images/bookmark-top.png](http://wiki.marinemap.googlecode.com/hg/images/bookmark-top.png)

Option B


![http://wiki.marinemap.googlecode.com/hg/images/bookmark-tools.png](http://wiki.marinemap.googlecode.com/hg/images/bookmark-tools.png)

I'm (Chad) leaning towards Option B right now. The top menu icons have so far been limited to navigating panels rather than _functions_, and adding a new icon to the top opens up question as to whether measurement or search might be included up there as well.

## Saving the Bookmark ##

![http://wiki.marinemap.googlecode.com/hg/images/bookmark-create.png](http://wiki.marinemap.googlecode.com/hg/images/bookmark-create.png)

As with all feature classes, we need a name. An optional description makes sense too, as this will hopefully become quite the communication tool.

I added a feature to the end of the form that somehow looks for feature classes displayed and explains to the user that these won't be visible to all users. Whether the feature is shared or not is pertinent to display here.

## After Save and the Attributes View ##

After saving or whenever a user double clicks the bookmark naturally the "Attributes" panel content will come up.

![http://wiki.marinemap.googlecode.com/hg/images/bookmark-attributes.png](http://wiki.marinemap.googlecode.com/hg/images/bookmark-attributes.png)

This view gives the user a url to copy, as well as alerting them to potential problems with sharing this link with unauthenticated users.

## Sharing ##

Sharing via groups can be handled just like any other feature. The difference though, is that it would be great to alert users to problems with sharing preferences on viewed features vs what groups they are trying to share the bookmark with.

# Technical Challenges #

  * kmltree already has support for serializing a tree's state via kmltree.getState(), but has no analogous setState. This would have to be added. There is already a restoreState private method, but this would have to exposed and extensively tested.
  * kmltreeManager should be extended to expose it's list of active instances of kmltree, and possibly add a manager-level getState and setState function.
  * The state of MyShapes and ShareWithMe change based on user, so there is no way to use kmltree to manage these features. Not sure how to deal with this yet.
  * The sharing views are not very extensible AFAIK. This would make it hard to check for unshared features in the view while sharing a bookmark. Maybe this can be handled on the backend as a form validation measure and the share form set via the rest config?
  * Sharing with un-authenticated users via link is so problematic and potentially confusing for users that it would be worth considering whether it's even needed. Maybe this could be a phase 2 bookmarks project.

## Bookmarks Involving Feature Classes ##

Feature Classes, such as AOIs, are an important component to support with bookmarks. However, there are unique technical challenges when dealing with them that may require that we implement bookmarks in phases and exclude them from the first phase.

For example, a user may want to share a bookmark that shows their AOI at a certain angle in relation to the depth contour layer in order to help describe how the depth at a location influenced the shape of their AOI. While storing the map extent, zoom level, and active layers (depth contour) within a bookmark is straightforward, including the AOI is not. We have to consider whether the AOI is shared with other users viewing the bookmark. That will require some additional checks and validation of new bookmarks. We also have to consider that while the bookmarked AOI shows up in the originating user's "My Shapes" tab, for other users it will be nested somewhere within a group in the "Shared With Me" tab. This difference in the way content is structured across users significantly increases the development time necessary to support this feature.

Since each feature has a unique ID, it should be possible to store within the bookmark a linked list of feature IDs representing features that are bookmarked, and their relation to groups and users. Then on the client side the contents of the relavent kmltrees can be traversed in order to expand and toggle folders and networklinks. This traversal process is possible but will be complex and require extensive testing. For this reason we would expect a **Phase 2 that adds Feature support to Map Bookmarks to take on the order of 120-160 hours to support**. There are no technical or efficiency reasons why we can't implement data layer and map extent bookmarking as a first phase and then add this support later.


### Icon Concepts ###

![http://commondatastorage.googleapis.com/marinemap/map_bookmark.png](http://commondatastorage.googleapis.com/marinemap/map_bookmark.png)