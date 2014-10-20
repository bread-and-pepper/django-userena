# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserenaSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_active', models.DateTimeField(help_text='The last date that the user was active.', null=True, verbose_name='last active', blank=True)),
                ('activation_key', models.CharField(max_length=40, verbose_name='activation key', blank=True)),
                ('activation_notification_send', models.BooleanField(default=False, help_text='Designates whether this user has already got a notification about activating their account.', verbose_name='notification send')),
                ('email_unconfirmed', models.EmailField(help_text='Temporary email address when the user requests an email change.', max_length=75, verbose_name='unconfirmed email address', blank=True)),
                ('email_confirmation_key', models.CharField(max_length=40, verbose_name='unconfirmed email verification key', blank=True)),
                ('email_confirmation_key_created', models.DateTimeField(null=True, verbose_name='creation date of email confirmation key', blank=True)),
                ('user', models.OneToOneField(related_name=b'userena_signup', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'userena registration',
                'verbose_name_plural': 'userena registrations',
            },
            bases=(models.Model,),
        ),
    ]
