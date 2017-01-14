FROM chuckus/python-2.7-alpine-pandas

RUN apk update \
  && apk add --virtual build-deps libc-dev python-dev gcc python-dev musl-dev \
  && apk add postgresql-dev \
  && pip install psycopg2 \
  && pip install Babel==2.0  \
  && pip install Django==1.8.3 \
  && pip install Jinja2==2.8 \
  && pip install MarkupSafe==0.23 \
  && pip install Pygments==2.0.2 \
  && pip install Sphinx==1.3.1 \
  && pip install alabaster==0.7.6 \
  && pip install coverage==3.7.1 \
  && pip install django-autoslug==1.8.0 \
  && pip install django-bulk-update==1.1.5 \
  && pip install django-common-helpers==0.7.0 \
  && pip install django-cors-headers==1.1.0 \
  && pip install django-debug-toolbar==1.3.2 \
  && pip install django-decorator-include==0.1 \
  && pip install django-simple-history==1.6.3 \
  && pip install django-tastypie==0.13.3 \
  && pip install docutils==0.12 \
  && pip install ecdsa==0.13 \
  && pip install jsonfield==1.0.3 \
  && pip install python-dateutil==2.4.2 \
  && pip install python-mimeparse==0.1.4 \
  && pip install pytz==2015.6 \
  && pip install six==1.10.0 \
  && pip install snowballstemmer==1.2.0 \
  && pip install sphinx-rtd-theme==0.1.8 \
  && pip install sqlparse==0.1.16 \
  && pip install wsgiref==0.1.2 \
  && pip install xlrd==0.9.4 \
  && pip install django-waffle==0.11 \
  && apk del build-deps

RUN ln -s /usr/bin/gcc-5.3.0-r0 /usr/bin/gcc

WORKDIR '/rhizome'
