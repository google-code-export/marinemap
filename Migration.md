# Introduction #

Schemas change. Deploying new version of the software is a pain if the schemas need to modified on a production database.

Migration is the solution - migration scripts explicitly describe the schema and database changes necessary allowing you to apply these changes to a production databases.


# Details #
In some respects, using migration scripts simply shifts the burden for handling schema and data migrations to the development process. In other words, development is a little tricker but deployment becomes much easier.

South migration **does** change the development workflow significantly so pay attention.

## Initial Steps for pre-existing codebase ##

For every machine that has a pre-migration copy of the codebase

  * First, install [South](http://south.aeracode.org/):

```
sudo easy_install south
```

  * Do an `svn update` on marinemap; anything after [revision 1376](https://code.google.com/p/marinemap/source/detail?r=1376) will have south added to your `INSTALLED_APPS` and ready to go.

  * South needs to add a table to your db. If you're comfortable running `syncdb`, do it now. Otherwise, run `manage.py dbshell` to load South-related tables into the db using the following SQL command (for south 0.7):

```
BEGIN;
CREATE TABLE "south_migrationhistory" (
    "id" serial NOT NULL PRIMARY KEY,
    "app_name" varchar(255) NOT NULL,
    "migration" varchar(255) NOT NULL,
    "applied" timestamp with time zone NOT NULL
)
;
COMMIT;
```


  * Assuming your tables and models are currently in sync, there are no _real_ migrations that need to take place. However, you will need to _fake_ the migrations to put each app under control of south.

```
./manage.py migrate --fake  
```



## Initial steps for a brand new installation ##

  * First, install [South](http://south.aeracode.org/):

```
sudo easy_install south
```

  * Do an `svn checkout` on marinemap

  * Run syncdb as normal

## Changing the schema ##

Anytime you make a change to an existing django model or add a model which requires database schema changes:

  * Change the model, test it, etc

  * Run the schemamigration command to auto-generate a migration script

```
manage.py schemamigration appname --auto
```

  * If there are any warnings, pay close attention and go back to step 1 if needed.

  * Run the migration

```
manage.py migrate appname
```

  * Check the migration script into svn

```
svn add lingcod/appname/migrations/0002_auto__add_field_appname_fieldnames.py
svn commit -m "Added field to appname"
```

  * Alert other developers than schema needs to be migrated

## Adding new apps ##

This is almost identical to "changing the schema" section above except for the `schemamigration` command.

  * Create a new app, models, etc and test it.

  * Run the startmigration command to auto-generate the initial migration script

```
manage.py startmigration new_app --initial 
```

  * If there are any warnings, pay close attention and go back to step 1 if needed.

  * Run the migration

```
manage.py migrate new_app
```

  * Check the everything into svn.

  * Alert other developers than schema needs to be migrated

## Applying migrations from other developers (includes deploying on production) ##

Assuming the devs followed the steps above:

  * Do an `svn update` on the codebase

  * Review all unapplied migrations. Use the `manage.py migrate --list` command and find any migrations without a `(*)` preceding it (unapplied migrations will show `( )`).

  * Run `manage.py migrate appname` for all apps that need migrating. Have a ton of mew migrations and just want to apply them all in a single command? A straight `manage.py migrate` will do this for **all** outstanding migrations.


