#!/bin/bash

python ./manage.py syncdb --noinput
python ./manage.py migrate --noinput

python ./manage.py runserver 0.0.0.0:9090
