# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

""" I need to go from:

BEGIN;
CREATE TABLE "userena_userenauser" (
    "user_id" integer NOT NULL PRIMARY KEY REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "last_active" timestamp with time zone,
    "activation_key" varchar(40) NOT NULL,
    "activation_key_created" timestamp with time zone,
    "activation_notification_send" boolean NOT NULL,
    "email_unconfirmed" varchar(75) NOT NULL,
    "email_confirmation_key" varchar(40) NOT NULL,
    "email_confirmation_key_created" timestamp with time zone
)
;
COMMIT;

"""

""" To:

BEGIN;
CREATE TABLE "userena_userena" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "last_active" timestamp with time zone,
    "activation_key" varchar(40) NOT NULL,
    "activation_notification_send" boolean NOT NULL,
    "email_unconfirmed" varchar(75) NOT NULL,
    "email_confirmation_key" varchar(40) NOT NULL,
    "email_confirmation_key_created" timestamp with time zone
)
;
COMMIT;

"""

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('userena_userenauser', 'userena_userena')
        db.add_column('userena_userena', 'id', models.IntegerField(default=-1), keep_default=False)
        db.delete_primary_key('userena_userena')
        db.create_primary_key('userena_userena', ['id',])
        db.delete_column('userena_userena', 'activation_key_created')

    def backwards(self, orm):
        db.rename_table('userena.userena', 'userena.userenauser')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'userena.userenauser': {
            'Meta': {'object_name': 'UserenaUser', '_ormbases': ['auth.User']},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'activation_key_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'activation_notification_send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_confirmation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email_confirmation_key_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email_unconfirmed': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'last_active': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['userena']
