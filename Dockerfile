FROM chuckus/python-2.7-alpine-pandas

RUN apk update \
  && apk add --virtual build-deps libc-dev python-dev gcc python-dev musl-dev \
  && apk add postgresql-dev \
  && pip install psycopg2==2.6.1 \
  && apk del build-deps

COPY ./requirements.txt /tmp/

RUN pip install --requirement /tmp/requirements.txt

RUN ln -s /usr/bin/gcc-5.3.0-r0 /usr/bin/gcc

WORKDIR '/rhizome'
