# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField(verbose_name='body')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='sent at')),
                ('sender_deleted_at', models.DateTimeField(null=True, verbose_name='sender deleted at', blank=True)),
            ],
            options={
                'ordering': ['-sent_at'],
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
        ),
        migrations.CreateModel(
            name='MessageContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_message', models.ForeignKey(verbose_name='latest message', to='umessages.Message')),
                ('um_from_user', models.ForeignKey(related_name='um_from_users', verbose_name='from user', to=settings.AUTH_USER_MODEL)),
                ('um_to_user', models.ForeignKey(related_name='um_to_users', verbose_name='to user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['latest_message'],
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='MessageRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read_at', models.DateTimeField(null=True, verbose_name='read at', blank=True)),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='recipient deleted at', blank=True)),
                ('message', models.ForeignKey(verbose_name='message', to='umessages.Message')),
                ('user', models.ForeignKey(verbose_name='recipient', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'recipient',
                'verbose_name_plural': 'recipients',
            },
        ),
        migrations.AddField(
            model_name='message',
            name='recipients',
            field=models.ManyToManyField(related_name='received_messages', verbose_name='recipients', through='umessages.MessageRecipient', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(related_name='sent_messages', verbose_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='messagecontact',
            unique_together=set([('um_from_user', 'um_to_user')]),
        ),
    ]
