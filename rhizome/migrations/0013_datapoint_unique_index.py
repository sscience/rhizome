# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from rhizome.models import DataPoint, Campaign
from pandas import DataFrame
import math
import pandas as pd
from rhizome.agg_tasks import AggRefresh
from django.db import transaction
from django.db.transaction import TransactionManagementError


# helper function for upsert_unique_indices
def add_unique_index(x):
    if x['campaign_id'] and not math.isnan(x['campaign_id']):
        x['unique_index'] = str(x['location_id']) + '_' + str(x['indicator_id']) + '_' + str(x['campaign_id'])
    else:
        x['unique_index'] = str(x['location_id']) + '_' + str(x['indicator_id']) + '_' + str(pd.to_datetime(x['data_date'], utc=True))
    return x    

def upsert_unique_indices(apps, schema_editor):
    datapoint_values_list = ['id','created_at','indicator_id','location_id','campaign_id','data_date']
    historical_dps = DataFrame(list(DataPoint.objects.filter(unique_index = -1)\
        .values_list('id','created_at','indicator_id','location_id','campaign_id','data_date')), columns=datapoint_values_list)
    # create the unique index
    historical_dps = historical_dps.apply(add_unique_index, axis=1)

    # group by and max on created at, get the most recent upload
    historical_dps = historical_dps.sort("data_date", ascending=False).groupby("unique_index", as_index=False).first()

    # get the ids into a list and select them
    dps_to_update = DataPoint.objects.filter(id__in=list(historical_dps['id']))
    print 'dps to update'
    print len(dps_to_update)
    # then run a query and update each
    for dp in dps_to_update:
        unique_index = historical_dps[historical_dps['id'] == dp.id].iloc[0]['unique_index']
        dp.unique_index = unique_index
        dp.save()
    
    # delete all the other duplicates
    dps_to_delete = DataPoint.objects.filter(unique_index=-1)
    print 'dps_to_delete'
    print len(dps_to_delete)
    dps_to_delete.delete()

def run_agg_refresh(apps, schema_editor):
    campaigns = Campaign.objects.all()
    print 'len(campaigns)'
    print len(campaigns)
    for campaign in campaigns:
        ar = AggRefresh(campaign.id)
        # try/except block hack because tests fail otherwise
        try:
            with transaction.atomic():
                ar.main()
        except TransactionManagementError as e:
            print 'error'
            pass
    raise Exception("not done writing migration!")


class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0012_datapoint_campaign_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='unique_index',
            field=models.CharField(default=-1, max_length=255),
        ),
        migrations.AddField(
            model_name='historicaldatapointentry',
            name='unique_index',
            field=models.CharField(default=-1, max_length=255, db_index=True),
        ),
        migrations.RunPython(upsert_unique_indices),
        # # update field constraint
        # migrations.AlterField(
        #     model_name='datapoint',
        #     name='unique_index',
        #     field=models.CharField(default=-1, max_length=255,unique=True),
        # ),
        # run agg_refresh
        migrations.RunPython(run_agg_refresh)
    ]

