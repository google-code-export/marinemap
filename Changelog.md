# Release Notes #

## REL-1.1 ##

  * Added Ecotrust Impact Analysis for MPAs. ????
  * Added attachment upload capability for array proposals. [r1214](https://code.google.com/p/marinemap/source/detail?r=1214)
  * New users can register themselves rather than requesting accounts via email. [r1218](https://code.google.com/p/marinemap/source/detail?r=1218)
  * User profile page. Allows users to change their email address and correct their name, as well as see what groups they belong to. [r1256](https://code.google.com/p/marinemap/source/detail?r=1256)
  * Links in About page now all open in new windows. [r1192](https://code.google.com/p/marinemap/source/detail?r=1192)
  * Showing first and last names rather than username in sharing form. [r1203](https://code.google.com/p/marinemap/source/detail?r=1203)
  * Various fixes to the sorting of habitats, bioregions and clusters in reports. [r1205](https://code.google.com/p/marinemap/source/detail?r=1205), [r1197](https://code.google.com/p/marinemap/source/detail?r=1197), [r1196](https://code.google.com/p/marinemap/source/detail?r=1196)
  * Changed all references to help@lists.marinemap.org to help@marinemap.org. [r1280](https://code.google.com/p/marinemap/source/detail?r=1280)
  * Added python API documentation
  * Improvements to test coverage

### New Dependencies in REL-1.1 ###

  * [django-registration 0.8alpha](http://bitbucket.org/ubernostrum/django-registration/downloads/)

### Schema Changes ###

```

BEGIN;
CREATE TABLE "registration_registrationprofile" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "activation_key" varchar(40) NOT NULL
)
;
ALTER TABLE mlpa_mpaarray ADD COLUMN "supportfile1" varchar(100);
ALTER TABLE mlpa_mpaarray ADD COLUMN "supportfile2" varchar(100);
ALTER TABLE staticmap_mapconfig ADD COLUMN "default_srid" integer NOT NULL DEFAULT 4326;
ALTER TABLE mlpa_mpaarray ADD COLUMN "short_name" varchar(8);

CREATE TABLE "econ_analysis_fishingimpactanalysismap_allowed_uses" (
    "id" serial NOT NULL PRIMARY KEY,
    "fishingimpactanalysismap_id" integer NOT NULL,
    "alloweduse_id" integer NOT NULL REFERENCES "mlpa_alloweduse" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("fishingimpactanalysismap_id", "alloweduse_id")
)
;
CREATE TABLE "econ_analysis_fishingimpactanalysismap_allowed_targets" (
    "id" serial NOT NULL PRIMARY KEY,
    "fishingimpactanalysismap_id" integer NOT NULL,
    "allowedtarget_id" integer NOT NULL REFERENCES "mlpa_allowedtarget" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("fishingimpactanalysismap_id", "allowedtarget_id")
)
;
CREATE TABLE "econ_analysis_fishingimpactanalysismap" (
    "id" serial NOT NULL PRIMARY KEY,
    "group_name" text NOT NULL,
    "group_abbr" text NOT NULL,
    "port_name" text NOT NULL,
    "port_abbr" text NOT NULL,
    "species_name" text NOT NULL,
    "species_abbr" text NOT NULL,
    "cell_size" integer NOT NULL
)
;
ALTER TABLE "econ_analysis_fishingimpactanalysismap_allowed_uses" ADD CONSTRAINT "fishingimpactanalysismap_id_refs_id_18cc7946" FOREIGN KEY ("fishingimpactanalysismap_id") REFERENCES "econ_analysis_fishingimpactanalysismap" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "econ_analysis_fishingimpactanalysismap_allowed_targets" ADD CONSTRAINT "fishingimpactanalysismap_id_refs_id_f41d20e1" FOREIGN KEY ("fishingimpactanalysismap_id") REFERENCES "econ_analysis_fishingimpactanalysismap" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "econ_analysis_fishingimpactstats" (
    "id" serial NOT NULL PRIMARY KEY,
    "map_id" integer NOT NULL UNIQUE REFERENCES "econ_analysis_fishingimpactanalysismap" ("id") DEFERRABLE INITIALLY DEFERRED,
    "totalCells" integer NOT NULL,
    "srCells" integer NOT NULL,
    "totalArea" double precision NOT NULL,
    "srArea" double precision NOT NULL,
    "totalValue" double precision NOT NULL,
    "srValue" double precision NOT NULL
)
;
CREATE TABLE "econ_analysis_fishingimpactresults" (
    "id" serial NOT NULL PRIMARY KEY,
    "mpa_id" integer NOT NULL REFERENCES "mlpa_mlpampa" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group" text NOT NULL,
    "port" text NOT NULL,
    "species" text NOT NULL,
    "perc_value" double precision NOT NULL,
    "perc_area" double precision,
    "date_modified" timestamp with time zone NOT NULL
)
;
COMMIT;


```

### Missed Targets ###

  * Internet Explorer 8 support will not be included in this version. We're still working on a fix, but it won't be available until the [1.2 release](http://marinemap-reporting.appspot.com/#Milestone-1-2) on April 19th.