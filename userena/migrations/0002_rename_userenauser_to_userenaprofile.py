# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('userena_userenauser', 'userena_userenaprofile')

    def backwards(self, orm):
        db.rename_table('userena_userenaprofile', 'userena_userenauser')
