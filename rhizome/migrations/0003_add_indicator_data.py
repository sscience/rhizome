# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jsonfield.fields
import django.db.models.deletion
from django.db import models, migrations
from django.conf import settings
from django.db.models import get_app, get_models
from django.db.utils import IntegrityError
import pandas as pd

from rhizome.cache_meta import minify_geo_json, LocationTreeCache

from rhizome.models.document_models import Document, SourceObjectMap, \
    DocumentSourceObjectMap, DocumentDetail, DocDetailType
from rhizome.models.indicator_models import IndicatorTag, Indicator
from rhizome.models.location_models import Location, LocationTree, LocationType
from rhizome.models.datapoint_models import DataPoint

def populate_source_data(apps, schema_editor):
    '''
    Here, we take an excel file that has the same schema as the database
    we lookup the approriate model and bulk insert.
    We need to ingest the data itself in the same order as the excel
    sheet otherwise we will have foreign key constraint issues.
    '''

    source_sheet_df = pd.read_csv('migration_data/informal_settlements.csv', \
        encoding = 'iso8859_6') # Arabic


    source_sheet_df.drop(source_sheet_df.index[:1], inplace=True)

    mdf = MetaDataGenerator(source_sheet_df)
    mdf.main()

    ## populate the location tree @
    ltc = LocationTreeCache()
    ltc.main()

    if len(LocationTree.objects.all().values_list('id', flat=True)) == 0:
        raise Exception('Location Tree Empty')

    if len(DataPoint.objects.all().values_list('id', flat=True)) == 0:
        raise Exception('No Datapoints')


class MetaDataGenerator:

    def __init__(self, source_sheet_df):

        self.country = 'Lebanon'
        # self.campaign_type = CampaignType.objects.get(name='IDP Survey')
        self.source_sheet_df = source_sheet_df
        self.source_sheet_df['COUNTRY'] = self.country # FIXME get from settings

        self.country_location_type, created = \
            LocationType.objects.get_or_create(name='Country', defaults={'admin_level':0})
        self.top_lvl_location, created = Location.objects\
            .get_or_create(name = self.country,\
                defaults = {'location_type_id': self.country_location_type.id})

        self.odk_file_map = {
            'date_column': 'Date the site was created',
            'lat_column': 'Latitude',
            'lon_column': 'Longitude',
            'province_column': 'Governorate',
            'district_column': 'Cadastral',
            'settlement_column': 'Local Name'
        }

        LocationType.objects.get_or_create(name = 'Province', defaults={'admin_level': 1})
        LocationType.objects.get_or_create(name = 'District', defaults={'admin_level': 2})
        LocationType.objects.get_or_create(name = 'Settlement', defaults={'admin_level': 3})

        self.admin_level_parent_lookup = {
            # 'Province' : 'COUNTRY',
            'District' : 'Governorate',
            'Settlement' : 'Cadastral'
        }

        ## add location_ids here when inserting and use to find the parent ##
        self.existing_location_map = {self.country : self.top_lvl_location.id}

        # Aakkar
        # An Nabaţīya
        # Baalbek-Hermel
        # Beirut
        # Beqaa	LB.BQ
        # Mount Lebanon
        # North Lebanon'
        # South Lebanon

        ## the names in the shape file are different from ODK ##
        # { ODK_NAME: HIGH_CHART_NAME }
        self.location_lookup = {
            }

        self.indicator_lookup = {
            'RRM_Distribution/group_distribution/rrm_kits': 'RRM Kits Distributed',
            'RRM_Distribution/group_distribution/plumpy' : 'Plumpy Bars Distributed',
            'RRM_Distribution/group_distribution/families': 'Families Seen',
            'RRM_Distribution/group_distribution/singles': 'Singles Seen'
        }

    def main(self):

        self.document =  Document.objects.create(doc_title = 'lbn_initial',
                            guid = 'lbn_initial')

        self.build_meta_data_from_source() ## creates the geo heirarchy
        self.process_source_sheet() ## creates the datapoints

    def build_meta_data_from_source(self):

        indicator_ids = self.build_indicator_meta()
        location_ids = self.build_location_meta()

    def build_indicator_meta(self):

        batch = []

        df_columns = self.source_sheet_df.columns
        config_columns = self.odk_file_map.values()
        indicators = df_columns #set(df_columns).intersection(set(config_columns))

        for ind in indicators:

            try:
                ind_name = self.indicator_lookup[ind]
                ind_obj = Indicator.objects.create(**{
                    'name':ind_name,
                    'short_name':ind_name,
                    'description':ind_name
                })
                som_obj = SourceObjectMap.objects.create(**{
                    'master_object_id': ind_obj.id,
                    'content_type': 'indicator',
                    'source_object_code': ind
                })

                doc_som = DocumentSourceObjectMap.objects.create(
                    document_id = self.document.id,
                    source_object_map_id = som_obj.id
                )

            except KeyError:
                pass

    def build_location_meta(self):

        ## PROVINCE ##
        ## since we ingested the shapes first, we lookup the province name,
        ## then change it to what the ODK form has.. this allows us to attach
        ## the shapes to the location IDS from ODK so that they are familiar
        ## to the owners of the data

        province_column = self.odk_file_map['province_column']
        province_df = pd.DataFrame(self.source_sheet_df[province_column])

        province_column = self.odk_file_map['province_column']
        for ix, row in province_df.iterrows():

            row_dict = row.to_dict()

            province_name = row_dict[province_column]

            try:

                existing_location_name = self.location_lookup[province_name]

                location_obj = Location.objects\
                    .get(name = existing_location_name)

            except KeyError:
                location_obj, created = Location.objects.get_or_create(
                    name = province_name,
                    defaults = {
                    'location_code': province_name,
                    'parent_location_id': self.top_lvl_location.id,
                    'location_type_id': LocationType.objects\
                        .get(name = 'Province').id
                })
            self.existing_location_map[province_name] = location_obj.id

        # DISTRICT ##
        district_column = self.odk_file_map['district_column']
        district_df = pd.DataFrame(\
            self.source_sheet_df[[district_column,province_column]])

        district_df.drop_duplicates(inplace=True)
        self.process_location_df(district_df, 'District')

        ## SETTlEMENT ##
        settlement_column = self.odk_file_map['settlement_column']
        settlement_df = pd.DataFrame(\
            self.source_sheet_df[[settlement_column,district_column]])

        settlement_df.drop_duplicates(inplace=True,subset=[settlement_column])
        self.process_location_df(settlement_df, 'Settlement')

        ## this wil lmake it so we can ingest data
        source_object_map_batch = [SourceObjectMap(**{
            'master_object_id': loc.id,
            'content_type': 'location',
            'source_object_code': loc.location_code
        }) for loc in Location.objects.all()]
        # SourceObjectMap.objects.bulk_create(source_object_map_batch)

        ## now let me change the names of the locations
        ##  so that they are familiar to the progam

        for k,v in self.location_lookup.iteritems():

            try:
                l = Location.objects.get(name=v)
                l.name = k
                l.location_code = k
                l.save()
            except Location.DoesNotExist:  ## LOOK INTO THIS....
                pass

    def process_location_df(self, location_df, admin_level):

        location_type_id = LocationType.objects.get(name = admin_level).id
        location_name_column = self.odk_file_map[admin_level.lower() + '_column']

        batch = []

        try:
            parent_column = self.admin_level_parent_lookup[admin_level]
            location_df['parent'] = location_df[parent_column]
        except KeyError:
            location_df['parent'] == self.country

        for ix, loc in location_df.iterrows():

            loc_dict = loc.to_dict()

            try:
                ## If a district comes in but there is a province with that
                ## name as well, we concat the name with the admin level in the
                ## except.
                existing_location_id = \
                    self.existing_location_map[loc[location_name_column]]
                location_code = unicode(loc[location_name_column]) + ' - ' + \
                    unicode(admin_level)
            except KeyError:
                location_code = loc[location_name_column]

            # batch.append(\
            Location.objects.create(**{
                'name': location_code,
                'location_code': location_code,
                'parent_location_id': self.existing_location_map[loc['parent']],
                'location_type_id': location_type_id
            })
            # )

        # Location.objects.filter(location_type__name=admin_level).delete()
        # Location.objects.bulk_create(batch)

        ## now add these ids to the parent map for later lookups ##
        location_name_to_id_list_of_lists = list(Location.objects\
            .filter(location_type_id=location_type_id)\
            .values_list('location_code','id'))

        for locName, locId in location_name_to_id_list_of_lists:
            self.existing_location_map[locName] = locId

        for k,v in self.existing_location_map.iteritems():
            som_obj, created = SourceObjectMap.objects.get_or_create(
                content_type = 'location',
                source_object_code = k,
                defaults = {'master_object_id': v}
            )
            doc_som_obj, created = DocumentSourceObjectMap.objects.get_or_create(
                source_object_map_id = som_obj.id,
                document_id = self.document.id
            )
    ## make source object maps ##
    def model_df_to_data(model_df,model):

        meta_ids = []

        non_null_df = model_df.where((pd.notnull(model_df)), None)
        list_of_dicts = non_null_df.transpose().to_dict()

        for row_ix, row_dict in list_of_dicts.iteritems():

            row_id = model.objects.create(**row_dict)
            meta_ids.append(row_id)

        return meta_ids


    def process_source_sheet(self):

        create_doc_details(self.document.id)

        ## document -> source_submissions ##
        # FiXME -- replace with "transform_upload"
        self.document.location_column = self.odk_file_map['settlement_column']
        self.document.date_column = self.odk_file_map['date_column']
        self.document.lat_column = self.odk_file_map['lat_column']
        self.document.lon_column = self.odk_file_map['lat_column']
        self.document.uq_id_column = 'PCode'
        self.document.existing_submission_keys = []
        self.document.file_header = list(self.source_sheet_df.columns)
        self.document.csv_df = self.source_sheet_df
        self.document.process_file()
        self.document.upsert_source_object_map()

        ## source_submissions -> datapoint ##
        self.document.refresh_master()


def create_doc_details(doc_id):

    doc_detail_types = ['uq_id_column', 'date_column', 'location_column', \
        'lat_column', 'lon_column']

    for dd_type in doc_detail_types:

        ddt = DocDetailType.objects.create(name = dd_type)

        DocumentDetail.objects.create(
            document_id = doc_id,
            doc_detail_type_id = ddt.id,
            doc_detail_value = dd_type ## this implies that the source columns
                                        ## are named with the above convention
        )

class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0002_add_geo_data'),
    ]

    operations = [
        migrations.RunPython(populate_source_data),
        ]
