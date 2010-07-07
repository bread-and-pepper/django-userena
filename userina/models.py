from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from userina import settings as userina_settings

import datetime, random, re
from dateutil.relativedelta import relativedelta

SHA1_RE = re.compile('^[a-f0-9]{40}$')

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
        account = self.create(user=user,
                              verification_key=verification_key)
        account.send_verification_email()
        return account

    def verify_account(self, verification_key):
        """
        Verify a ``Account`` by supplying a valid ``verification_key``.

        """
        if SHA1_RE.search(verification_key):
            try:
                account = self.get(verification_key=verification_key)
            except self.Model.DoesNotExist:
                return False
            if not account.verification_key_expired():
                account.verification_key = userina_settings.USERINA_VERIFIED
                account.verified = True
                account.save()
                return account
        return False

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

    @property
    def get_verification_url(self):
        """ Making it simple to supply the verification URI """
        site = Site.objects.get_current()
        path = reverse('userina_verify',
                       kwargs={'verification_key': self.verification_key})
        return 'http://%(domain)s%(path)s' % {'domain': site.domain,
                                              'path': path}

    def verification_key_expired(self):
        """
        Returns ``True`` when the ``verification_key`` of the account is
        expired and ``False`` if the key is still valid.

        """
        return False

    def send_verification_email(self):
        """ Sends a verification e-mail to the user """
        site = Site.objects.get_current()
        context= {'account': self,
                  'verification_days': userina_settings.USERINA_VERIFICATION_DAYS,
                  'site': site}

        subject = render_to_string('userina/verification_email_subject.txt',
                                   context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('userina/verification_email_message.txt',
                                   context)
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
