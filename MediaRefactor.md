## Wish List ##

  * use Google Closure Compiler rather than jsmin for smaller files and compile-time warnings and error checking
  * require running the build step even when in debug mode so that errors don't crop up after compiling js and css assets
  * optionally automate builds whenever source files are changed
  * support more complex build steps like compiling SASS files (see http://code.google.com/p/kmltree)
  * more explicitly separate source files from end result that should be hosted. (no need to make the entire uncompressed src accessible)
  * support hosting on s3, and make moving media there easy
  * address testing in some way (run lingcod vs project tests separately or together?)
  * Save compiled javascript and style assets to the repository rather than requiring that they be built with each new install or update to the production machine(s)

## Big Picture stuff ##

So every app might have three types of media that need to be handled differently:

### 1) Compilable Source Files ###

Includes js and css files that can be compiled in various ways to produce smaller and fewer files for deployment. The optimal solution will gather all the compilable media (look at the assets setting?), build it (Google Closure, jsmin, etc) and push the deployable end-product to the proper location.

#### problems/questions ####

  * can google closure + SASS and Sprite build steps be integrated into django-compress?
  * if not a custom script should be easy, but can it be automated to recompile on changes to the source files?
  * will projects need to override built-in stylesheets or javascripts? if so how would that be accomplished? this kind of extensibility could alternatively be provided by js apis, "theme" css files, and just the cascading nature of css

### 2) Standard Media ###

There will be some stuff like images, shapefiles, etc which will just be served up verbatim. These just need to be collected and pushed to their proper locations.

### 3) User Uploads ###

User-uploaded files present an interesting challenge because, by default, django just throws them into MEDIA\_ROOT which means that access to the media cannot be controlled by django authentication! We need to rethink this - possibly define a UPLOAD\_MEDIA\_URL and UPLOAD\_MEDIA\_ROOT and a special view to handle reading them. This would require refactoring on some of the existing apps. (Related to [Issue 313](https://code.google.com/p/marinemap/issues/detail?id=313) and [Issue 314](https://code.google.com/p/marinemap/issues/detail?id=314))

## Reference Implementations ##

  * http://blog.brianbeck.com/post/50940622/collectmedia
  * http://www.djangosnippets.org/snippets/1068/ <- a little complex but seems like a good solution
  * https://groups.google.com/group/django-developers/browse_thread/thread/94efe43b1d1c7787
  * http://pypi.python.org/pypi/django-staticfiles (not too crazy about how many settings it requires. Seems to ignore useful conventions in django)
  * http://www.djangosnippets.org/snippets/1066/ <- like the simplicity, dislike that it doesn't have a clear mechanism for extension
  * http://djangoadvent.com/1.2/everything-i-hate-about-mingus/
  * http://code.google.com/p/django-appmedia/ <- I really don't like this one because it has custom templatetags rather than using the standard MEDIA\_URL setting


## Solution? ##

There doesn't appear to be a solution out there that handles all our needs. `collectmedia` is nice for what it does, but it do much other than copy over files to MEDIA\_ROOT.