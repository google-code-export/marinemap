We need a simple way to demonstrate Google Wave + Earth functionality in a standalone demo before integrating it into MarineMap. The goal is to make sure our design decisions are well grounded in what Wave can actually do, and communicate to others outside our team what we are trying to achieve.

## Desired Features ##

  * Wave and Earth side-by-side in the same application window
  * A way to sync the map camera to the Wave. This would add inline messages to the Wave announcing that a user has changed the map state. One should be able to roll back and forward thru changes to the map state with the Playback widget.
  * A way to post KML file to the Wave. These will be displayed in the application as a layer that can be toggled on/off. One should be able to roll back and forward to show how layers were toggled on/off thru time with the Playback widget. This should start as just posting of a publicly accessible url, but in the actual implementation we might support uploading a file like an "attachment" as well. In the future, it would be great if the widget could be expanded to show the entire kml tree such as folder contents.
  * A function to export the entire geographic contents of a wave as kml.

## Organization ##

This ought to start as a demo on it's own dedicated page under /media. Useful pieces of javascript code should be put into appropriate namespaces.

## Implementation ##

Google describes Wave as having 3 major components; the API, client application, and Wave federation protocol. While we may someday want to host a federation server, our extensions of Wave will not modify the protocol. We should also strive to limit customization of the client library where possible. Where most if not all our effort is going to be concentrated is in the Wave APIs.

### Embed API ###
http://code.google.com/apis/wave/embed/

We'll need this to stick waves in our application layout.

_Currently the embed api only support showing a wave, not the full list-view. This will be a problem if not resolved with a public API on Google's end_.

lol, one page of api docs:
http://code.google.com/apis/wave/embed/reference.html

### Robots API ###

http://code.google.com/apis/wave/extensions/robots/index.html

### Gadget API ###

http://code.google.com/apis/wave/extensions/gadgets/guide.html