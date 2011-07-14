from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from userena.models import UserenaLanguageBaseProfile

import datetime

class Profile(UserenaLanguageBaseProfile):
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
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)

    @property
    def age(self):
        if not self.birth_date: return False
        else:
            today = datetime.date.today()
            # Raised when birth date is February 29 and the current year is not a
            # leap year.
            try:
                birthday = self.birth_date.replace(year=today.year)
            except ValueError:
                day = today.day - 1 if today.day != 1 else today.day + 2
                birthday = self.birth_date.replace(year=today.year, day=day)
            if birthday > today: return today.year - self.birth_date.year - 1
            else: return today.year - self.birth_date.year
