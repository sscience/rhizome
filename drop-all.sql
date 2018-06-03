truncate table doc_datapoint;
truncate table agg_datapoint;
truncate table datapoint;
truncate table indicator cascade;
truncate table source_doc cascade;
truncate table source_object_map cascade;
truncate table location cascade;
truncate table location_tree cascade;

TRUNCATE TABLE django_migrations;

SELECT * FROM information_schema.tables
where table_name like '%auth%'

DROP TABLE "django_admin_log" CASCADE;
DROP TABLE "django_content_type" CASCADE;
DROP TABLE "django_migrations" CASCADE;

DROP TABLE IF EXISTS "auth_group" CASCADE;
DROP TABLE IF EXISTS  "auth_group_permissions" CASCADE;
DROP TABLE IF EXISTS "auth_user_groups" CASCADE;
DROP TABLE IF EXISTS "auth_permission" CASCADE;
DROP TABLE IF EXISTS "auth_user_user_permissions" CASCADE;
DROP TABLE IF EXISTS  "auth_user" CASCADE;


DROP TABLE IF EXISTS agg_datapoint

SELECT 'DROP TABLE IF EXISTS ' || table_name || ' CASCADE;' FROM information_schema.tables
WHERE table_schema = 'public';


DROP TABLE IF EXISTS corsheaders_corsmodel CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS custom_chart CASCADE;
DROP TABLE IF EXISTS custom_dashboard CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_user_groups CASCADE;
DROP TABLE IF EXISTS auth_user CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS auth_user_user_permissions CASCADE;
DROP TABLE IF EXISTS doc_detail_type CASCADE;
DROP TABLE IF EXISTS indicator_tag CASCADE;
DROP TABLE IF EXISTS indicator_bound CASCADE;
DROP TABLE IF EXISTS indicator_to_tag CASCADE;
DROP TABLE IF EXISTS doc_detail CASCADE;
DROP TABLE IF EXISTS doc_object_map CASCADE;
DROP TABLE IF EXISTS source_object_map CASCADE;
DROP TABLE IF EXISTS location_permission CASCADE;
DROP TABLE IF EXISTS location_polygon CASCADE;
DROP TABLE IF EXISTS location_tree CASCADE;
DROP TABLE IF EXISTS min_polygon CASCADE;
DROP TABLE IF EXISTS location_type CASCADE;
DROP TABLE IF EXISTS datapoint CASCADE;
DROP TABLE IF EXISTS datapoint_with_computed CASCADE;
DROP TABLE IF EXISTS doc_datapoint CASCADE;
DROP TABLE IF EXISTS source_doc CASCADE;
DROP TABLE IF EXISTS source_submission CASCADE;
DROP TABLE IF EXISTS campaign_type CASCADE;
DROP TABLE IF EXISTS location CASCADE;
DROP TABLE IF EXISTS agg_datapoint CASCADE;
DROP TABLE IF EXISTS tastypie_apikey CASCADE;
DROP TABLE IF EXISTS campaign CASCADE;
DROP TABLE IF EXISTS tastypie_apiaccess CASCADE;
DROP TABLE IF EXISTS indicator CASCADE;
DROP TABLE IF EXISTS waffle_sample CASCADE;
DROP TABLE IF EXISTS waffle_switch CASCADE;
DROP TABLE IF EXISTS waffle_flag_groups CASCADE;
DROP TABLE IF EXISTS waffle_flag CASCADE;
DROP TABLE IF EXISTS waffle_flag_users CASCADE;
DROP TABLE IF EXISTS calculated_indicator_component CASCADE;


