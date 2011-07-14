from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from userena.models import UserenaBaseProfile

import datetime

class Profile(UserenaBaseProfile):
    """ Default profile """
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )

    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')

    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)
    location =  models.CharField(_('location'), max_length=255, blank=True)
    about_me = models.TextField(_('about me'), blank=True)

class SecondProfile(UserenaBaseProfile):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile_second') 
