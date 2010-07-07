from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor

import datetime, random
from dateutil.relativedelta import relativedelta

class AccountManager(models.Manager):
    """ Extra functionality for the account manager. """
    def create_user(self, username, email, password):
        new_user = User.objects.create_user(username, email, password)
        new_user.save()

        account = self.create_account(new_user)
        return new_user

    def create_account(self, user):
        """
        Create a ``Account`` for a given ``User``.

        """
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        username = user.username
        if isinstance(username, unicode):
            username = username.encode('utf-8')
        verification_key = sha_constructor(salt+username).hexdigest()
        return self.create(user=user,
                           verification_key=verification_key)

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
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True, null=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)
    is_verified = models.BooleanField(_('verified'),
                                      default=False,
                                      help_text=_("Designates whether this user has verified his e-mail address."))
    verification_key = models.CharField(_('verification key'), max_length=40)

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

    def send_verification_email(self):
        """ Sends a verification e-mail to the user """
        pass

User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
