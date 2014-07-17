from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'polio.views.home', name='home'),

    # url(r'^uf04/datapoints/', ),
    url(r'^datapoints/', include('datapoints.app_urls.urls', namespace="datapoints")),
    url(r'^datapoints/indicators/', include('datapoints.app_urls.indicator_urls', namespace="indicators")),
    url(r'^datapoints/regions/', include('datapoints.app_urls.region_urls', namespace="regions")),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login, name='login'),

)