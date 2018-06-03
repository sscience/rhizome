# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import urllib2
import json

from django.db.models import get_app, get_models
from django.db import models, migrations, IntegrityError, transaction
import pandas as pd

from rhizome.models.location_models import Location, LocationPolygon,\
    LocationType
from rhizome.models.document_models import Document
from rhizome.cache_meta import minify_geo_json, LocationTreeCache

from django.conf import settings

from pprint import pprint


def populate_geo_data(apps, schema_editor):
    '''
    Here, we take an excel file that has the same schema as the database
    we lookup the approriate model and bulk insert.
    We need to ingest the data itself in the same order as the excel
    sheet otherwise we will have foreign key constraint issues.
    '''

    process_geo_json()


def process_geo_json():
    '''
    Depending on     the values put in the COUNTRY_LIST, we pull shapes from
    The highcharts map repository.  This will give us shapes for admin level 1
    for the countries we specify.
    '''

    country_list = ['af','ye']## settings.COUNTRY_LIST
    for c in country_list:
        create_country_meta_data(c)

    minify_geo_json()

def create_country_meta_data(c):

    json_file_name = 'migration_data/geo/{0}.json'.format(c)

     # if this file has not already been saved, fetch it from the below url
    if not os.path.isfile(json_file_name):

        url = 'http://code.highcharts.com/mapdata/countries/{0}/{0}-all.geo.json'.format(c)
        print 'FETCHING URL {0}'.format(url)
        print 'FETCHING URL {0}'.format(url)
        print 'FETCHING URL {0}'.format(url)
        print 'FETCHING URL {0}'.format(url)
        print 'FETCHING URL {0}'.format(url)

        response = urllib2.urlopen(url)

        data = json.loads(response.read())

        with open(json_file_name, 'w+') as outfile:
            json.dump(data, outfile)

    # create a dataframe where one rwo represents one shape #
    try:
        with open(json_file_name) as data_file:
            data = json.load(data_file)
            features = data['features']
            geo_json_df = pd.DataFrame(features)
    except IOError:
        return

    # create the country and province location types #
    country_lt, created = LocationType.objects.get_or_create(
        name = 'Country', admin_level = 0
    )
    province_lt, created = LocationType.objects.get_or_create(
        name = 'Province', admin_level = 1
    )

    # create the top level country #
    country_name = features[0]['properties']['country']
    country_loc_object = Location.objects.create(
        name = country_name,
        location_code = c,
        location_type_id = country_lt.id
    )

    for ix, row in geo_json_df.iterrows():

        process_geo_row(ix, row, country_loc_object, province_lt)

def process_geo_row(ix, row, country_loc_object, province_lt):

    # create the proivince location #
    row_properties, row_geo = row.properties, row.geometry

    try:
        province_dict = {
            'name': row_properties['name'],
            'parent_location_id': country_loc_object.id,
            'location_code': row.id,
            'location_type_id':province_lt.id
        }
    except KeyError as err: # not a location since it does not have name field
        print err

    loc_name = row_properties.get('name')
    if not loc_name:
        loc_name = row_properties.get('country')

    province_loc_object, created = Location.objects\
        .get_or_create(name=loc_name, defaults=province_dict)

    if not created: # high charts has dupes .. see parwan..

        # create the proivince shapes #
        LocationPolygon.objects.create(
            geo_json = row_geo, location_id = province_loc_object.id
        )


def model_df_to_data(model_df, model):

    meta_ids = []

    non_null_df = model_df.where((pd.notnull(model_df)), None)
    list_of_dicts = non_null_df.transpose().to_dict()

    for row_ix, row_dict in list_of_dicts.iteritems():

        row_id = model.objects.create(**row_dict)
        meta_ids.append(row_id)

    return meta_ids


class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_geo_data),
    ]
