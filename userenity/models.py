from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import datetime, dateutil

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

    def __unicode__(self):
        return u'%s' % self.user

    @models.permalink
    def get_absolute_url(self):
        pass

    @property
    def age(self):
        TODAY = datetime.date.today()
        return u'%s' % dateutil.relativedelta(TODAY, self.birth_date).years
