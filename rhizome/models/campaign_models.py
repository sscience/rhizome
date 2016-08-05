from django.db import models
from rhizome.models.location_models import Location
from rhizome.models.office_models import Office
from rhizome.models.indicator_models import IndicatorTag, Indicator

class CampaignType(models.Model):
    '''
    Each campaign must have a campaign_type_id.

    LPD ( low performing district )
    SNID ( Sub National Immunization Day )
    NID ( National Immunization Day )
    Mop Up ( Damage control after a case is found )

    '''

    name = models.CharField(max_length=55)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        db_table = 'campaign_type'


class Campaign(models.Model):
    '''
    A grouping of rhizome.  For polio, for we have a "campaign type" of
    "National Immunization Day" or "Mop Up" which means an immeiate response
    to a case by conncentrated vaccination campaigns in that area.

    The campaign thus allows you to model these two things with the model in
    these two instances:

    1. NID - Happens monthly for the Endemics.  We have a certain type of
    Inticators that we want to collect for this.. see "Management Dashboard."

        - indicator_list = Management Dashboard Indicators
        - top_lvl_location = Afghanistan

    2. Mop Up - Could happen anywhere where low immunity, for instance Ukraine.

        - indicator_list = A few select Indicators related to the "mop up"
        effort.  These will be different, put potentially overlapping from the
        NID indicator list.
        - top_lvl_location = Ukraine

    For other efforts, this model can be useful.. For Routine Immunization
    one could imagine a similar setup.

    The campaign model has a method called "get_datapoints", which gets the
    relevant raw and aggregated datapoints for a given campaign.  The data
    is aggregated from the date, indicator_list and location in the AggRefresh.

    The indicator_list, is determined by taking the flatened top lvl indicator
    tree that is for the campaign.
    '''

    name = models.CharField(max_length=255)
    top_lvl_location = models.ForeignKey(Location)
    top_lvl_indicator_tag = models.ForeignKey(IndicatorTag)
    office = models.ForeignKey(Office)
    campaign_type = models.ForeignKey(CampaignType)
    start_date = models.DateField()
    end_date = models.DateField()
    pct_complete = models.FloatField(default=.001)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaign'
        ordering = ('-start_date',)
        unique_together = ('office', 'start_date')

class CampaignToIndicator(models.Model):

    indicator = models.ForeignKey(Indicator)
    campaign = models.ForeignKey(Campaign)

    class Meta:
        db_table = 'campaign_to_indicator'
        unique_together = ('indicator', 'campaign')