"""
Django settings for polio project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

STATIC_URL = '/static/'
SITE_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '')
STATIC_ROOT = os.path.join(SITE_ROOT, '../static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

LOGIN_REDIRECT_URL = '/'

SECRET_KEY = 'asfafasfasfasfasfsafafasfasfkaf' os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'coverage',
    'simple_history',
    'rhizome',
    'tastypie',
    'corsheaders',
    'debug_toolbar',
    'waffle'
)

CORS_ORIGIN_ALLOW_ALL = True # should be upated to only allow our websites

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'waffle.middleware.WaffleMiddleware'
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'debug_toolbar.panels.sql.SQLPanel',

)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
)

ANONYMOUS_USER_ID = -1

ROOT_URLCONF = 'rhizome.urls'
WSGI_APPLICATION = 'rhizome.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'PORT': os.getenv('POSTGRES_PORT')
    }
}
# In the flexible environment, you connect to CloudSQL using a unix socket.
# Locally, you can use the CloudSQL proxy to proxy a localhost connection
# to the instance
DATABASES['default']['HOST'] = '/cloudsql/sudo-marketing:us-east1:notion-db'
if os.getenv('GAE_INSTANCE'):
    pass
else:
    DATABASES['default']['HOST'] = '127.0.0.1'

#
# ## we allow for connection either KOBO or APP ENGINE aggregate backends
# ODK_SETTINGS = {
#     'kobo': {
#         'KOBO_KEY': os.getenv('KOBO_KEY'),
#         'KOBO_SECRET': os.getenv('KOBO_KEY'),
#     },
#     'app_engine':{
#         # download here:
#         # https://opendatakit.org/downloads/download-info/odk-briefcase/
#         'JAR_FILE': '',
#         'RHIZOME_USERNAME': '',
#         # 'get an API key.. http://stackoverflow.com/questions/10940983/
#         'RHIZOME_KEY': '',
#         'STORAGE_DIRECTORY': '',  # /my/storage/dir',
#         'EXPORT_DIRECTORY': '',  # ' /my/output/dir,
#         'ODK_USER': '',  # my_odk_username
#         'ODK_PASS': '',  # my_odk_password
#         'AGGREGATE_URL': '',  # :'https://my-odk-server.appspot.com/',
#         'API_ROOT': 'http://localhost:8000/api/v1/',
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'EST'

# Template configuration
TEMPLATE_DIRS = (
   os.path.join(BASE_DIR, 'templates'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Our template directory
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

## API SETTINGS ##

TASTYPIE_DEFAULT_FORMATS = ['json']
API_LIMIT_PER_PAGE = 0
TASTYPIE_FULL_DEBUG = True

INTERNAL_IPS = ('127.0.0.1',)

# Flags for the Menu (SOP, C4D, Data)

## for a new instance -- put the 2 letter codes cooresponding to the countries
## you want to ingest maps for.  See here for more info http://code.highcharts.com/mapdata/
COUNTRY_LIST = os.getenv('COUNTRY_SHAPE_LIST', '').split(',')
## . 'http://code.highcharts.com/mapdata/countries/lb/lb-all.geo.json'
## . 'http://code.highcharts.com/mapdata/countries/sy/sy-all.geo.json'


######################
### FOR TESTING... ###
######################

# class DisableMigrations(object):
#
#     def __contains__(self, item):
#         return True
#
#     def __getitem__(self, item):
#         return "notmigrations"
#
# MIGRATION_MODULES = DisableMigrations()
# MEDIA_ROOT = 'rhizome/tests/_data/'
#
# DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
# DATABASES['default']['NAME'] = 'rhizome'
#
# USE_TZ = False
