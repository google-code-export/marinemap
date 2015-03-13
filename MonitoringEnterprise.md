# Introduction #

Outline for a marinemap-based application to coordinate sampling activity between various groups involved in sampling mpas and reference sites along the north-central CA coast.


# Details #

MP: I checked out the pyrifera models and there are some limitations when applying them to this project

  * Only point locations - most of the sampling sites specified are not nailed down to a single point location.
  * Focus on taxa-specific structured data - does not fit with the broader scope of socio+economic+ecological data integration that ME is focused on.
  * Focus on archiving well structured time-series data - doesnt appear that all ME research will fit into this schema.

Maybe each project will eventually have it's own schema for storing data. But the primary focus is to coordinate sampling that has disparate data schemas and has yet to occur (or is ongoing. Maybe what we need is a 'FutureSampling' or 'ProposedSamplingSite' model...

Psuedo-python code for CMS/V2 below

```

class Project:
    summary = CharField()
    objective = TextField()
    principals = TextField()
    contact = EmailField()
    ecosystem_Features = ForeignKey(EcosystemFeatures) # Or just text?
    key_metrics = ForeignKey(KeyMetrics) # Or just text?

SITE_CHOICES = (
    ('M', 'MPA Sampling Site'),
    ('R', 'Reference Sampling Site'),
)

class ProposedSamplingSite(models.PolygonFeatureClass):
    description = models.TextField()
    type = CharField(choices=SITE_CHOICES)
    start_date = DateTimeField()
    end_date = DateTimeField()

    class Meta:
        share = True
        form = ProposedSamplingSiteForm
        base_url = "/site/"
        show_template = "site/show.html"
        alternate_links = (
            ('samplesite.views.shapefile', 'Shapefile', 'single'),
            ('samplesite.views.multi_shapefile', 'aggregate Shapefile', 'multiple'),
            ('samplesite.views.kmz', 'as KMZ (Google Earth)', 'both')
        )
        edit_links = (
            ('samplesite.views.copy', 'Copy', 'both'),
        )
        

class ProposedSamplingSiteForm(forms.PolygonFeatureClassForm):
    class Meta(BaseArrayForm.Meta):
        model = ProposedSamplingSite


rest.register(ProposedSamplingSite)
```
