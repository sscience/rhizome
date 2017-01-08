#!/bin/bash

./manage.py syncdb --noinput
./manage.py migrate --noinput

python ./manage.py runserver 0.0.0.0:9090
