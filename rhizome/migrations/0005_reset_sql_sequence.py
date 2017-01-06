# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import os
from StringIO import StringIO

from django.core.management import call_command
from django.db import connection
from django.db.models.loading import get_app
from django.db import migrations

def reset_seq(apps, schema_editor):
    '''
    This has to do with Autoincrement... Since we insert PKs directly in
    "populate inital metadata", the DB engine still thinks that it needs
    to assign "1" to the first indicator fr instance that is created.

    By resetting the sequence, we ensure that the ORM will add add sequential
    IDs relative to what we created in the inital migrations
    '''

    os.environ['DJANGO_COLORS'] = 'nocolor'

    commands = StringIO()
    cursor = connection.cursor()

    for app in ['rhizome', 'django.contrib.auth']:
        try:
            label = app.split('.')[-1]
            if get_app(label):
                call_command('sqlsequencereset', label, stdout=commands)
        except Exception as err:
            pass
    try:
        cursor.execute(commands.getvalue())
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('rhizome', '0003_populate_initial_source_data'),
    ]

    operations = [
        migrations.RunPython(reset_seq),
    ]
