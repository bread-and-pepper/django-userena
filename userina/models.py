from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import datetime
from dateutil.relativedelta import relativedelta

class AccountManager(models.Manager):
    """ Extra functionality for the account manager """
    def create_user(self, **kwargs):
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        return None

class Account(models.Model):
    """
    A user account which stores all the nescessary information to have a full
    functional user implementation on your Django website.

    """
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    mugshot = models.FileField(_('mugshot'), upload_to='mugshots', blank=True)
    gender = models.PositiveSmallIntegerField(_('gender'), choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)

    objects = AccountManager()

    def __unicode__(self):
        return '%s' % self.user

    @models.permalink
    def get_absolute_url(self):
        pass

    @property
    def age(self):
        today = datetime.date.today()
        return relativedelta(today, self.birth_date).years

User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
