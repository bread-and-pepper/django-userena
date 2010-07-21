from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils.hashcompat import sha_constructor
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.mail import send_mail

from userina import settings as userina_settings
from userina.utils import get_gravatar

import datetime, random, re
from dateutil.relativedelta import relativedelta
from easy_thumbnails.fields import ThumbnailerImageField

SHA1_RE = re.compile('^[a-f0-9]{40}$')

def upload_to_mugshot(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERINA_MUGSHOT_PATH``

    """
    extension = filename.split('.')[-1]
    hash = sha_constructor(str(instance.user.id)).hexdigest()[:10]
    return '%(path)s%(hash)s.%(extension)s' % {'path': userina_settings.USERINA_MUGSHOT_PATH,
                                               'hash': hash,
                                               'extension': extension}

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
                              verification_key=verification_key,
                              verification_key_created=datetime.datetime.now())
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

                # Check to see if the account is new, or that it only need a
                # e-mail change.
                if account.temporary_email:
                    account.user.email = account.temporary_email
                    account.user.save()
                    account.temporary_email = ''
                else:
                    account.is_verified = True
                account.save()
                return account
        return False

    def notify_almost_expired(self):
        """
        Check for accounts that are ``USERINA_VERIFICATION_NOTIFY`` days before
        expiration.

        """
        if userina_settings.USERINA_VERIFICATION_NOTIFY:
            expiration_date = datetime.datetime.now() - datetime.timedelta(days=(userina_settings.USERINA_VERIFICATION_DAYS - userina_settings.USERINA_VERIFICATION_NOTIFY_DAYS))

            accounts = self.filter(is_verified=False,
                                   user__is_staff=False,
                                   verification_notification_send=False)
            notified_accounts = []
            for account in accounts:
                if account.verification_key_almost_expired():
                    account.send_expiry_notification()
                    notified_accounts.append(account)
            return notified_accounts

    def delete_expired_users(self):
        """
        Checks for expired accounts and delete's the ``User`` associated with
        it.

        Skips if the user ``is_staff``. Returns the deleted accounts.

        """
        accounts = self.filter(is_verified=False,
                               user__is_staff=False)
        deleted_users = []
        for account in accounts:
            if account.verification_key_expired():
                deleted_users.append(account.user)
                account.user.delete()
        return deleted_users

class Account(models.Model):
    """
    A user account which stores all the nescessary information to have a full
    functional user implementation on your Django website.

    """
    MUGSHOT_SETTINGS = {'size': (userina_settings.USERINA_MUGSHOT_SIZE,
                                 userina_settings.USERINA_MUGSHOT_SIZE),
                        'crop': 'smart'}
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    mugshot = ThumbnailerImageField(_('mugshot'),
                                    blank=True,
                                    upload_to=upload_to_mugshot,
                                    resize_source=MUGSHOT_SETTINGS)
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)
    location =  models.CharField(_('location'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)


    # Fields used for managing the account
    last_active = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(_('verified'),
                                      default=False,
                                      help_text=_('Designates whether this user has verified his e-mail address.'))
    verification_key = models.CharField(_('verification key'), max_length=40,
                                        blank=True)
    verification_key_created = models.DateTimeField(_('creation date of \
                                                      verification key'),
                                                    blank=True,
                                                    null=True)
    verification_notification_send = models.BooleanField(_('notification send'),
                                                         default=False,
                                                         help_text=_('Designates whether this user has already got a notification about verifying their account.'))
    temporary_email = models.EmailField(_('temporary_email'),
                                        blank=True,
                                        help_text=_('Temporary email address when the user requests an email change.'))

    objects = AccountManager()

    def __unicode__(self):
        return '%s' % self.user

    def save(self, *args, **kwargs):
        try:
            this = self.objects.get(id=self.id)
            if this.mugshot != self.mugshot:
                this.mugshot.delete()
        except: pass
        super(Account, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        pass

    @property
    def activity(self):
        """
        Returning the activity of the user

        @TIP: http://www.arnebrodowski.de/blog/482-Tracking-user-activity-with-Django.html

        """
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

        The key is either expired when the key is set to the value defined in
        ``USERINA_VERIFIED`` or ``verification_key_created`` is beyond the
        amount of days defined in ``USERINA_VERIFICATION_DAYS``.

        """
        expiration_days = datetime.timedelta(days=userina_settings.USERINA_VERIFICATION_DAYS)
        if self.verification_key == userina_settings.USERINA_VERIFIED:
            return True
        if datetime.datetime.now() >= self.verification_key_created + expiration_days:
            return True
        return False

    def verification_key_almost_expired(self):
        """
        Returns ``True`` when the ``verification_key`` is almost expired.

        """
        notification_days = datetime.timedelta(days=(userina_settings.USERINA_VERIFICATION_DAYS - userina_settings.USERINA_VERIFICATION_NOTIFY_DAYS))
        if datetime.datetime.now() >= self.verification_key_created + notification_days:
            return True
        return False

    def send_verification_email(self, new_email=False):
        """ Sends a verification e-mail to the user.

        If ``new_email`` is set to ``True`` than the user will get an
        verification email address to his ``temporary_email`` address. This way
        they can verify their new e-mail address.

        """
        new_account_templates = ['userina/emails/verification_email_subject.txt',
                                 'userina/emails/verification_email_message.txt']
        new_email_templates = ['userina/emails/verification_new_email_subject.txt',
                               'userina/emails/verification_new_email_message.txt']
        templates = new_email_templates if new_email else new_account_templates

        context= {'account': self,
                  'verification_days': userina_settings.USERINA_VERIFICATION_DAYS,
                  'site': Site.objects.get_current()}

        subject = render_to_string(templates[0], context)
        subject = ''.join(subject.splitlines())

        message = render_to_string(templates[1], context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.temporary_email if new_email else self.user.email,])

    def send_expiry_notification(self):
        """ Notify the user that his account is about to expire """
        context = {'account': self,
                   'days_left': userina_settings.USERINA_VERIFICATION_NOTIFY_DAYS,
                   'site': Site.objects.get_current()}

        subject = render_to_string('userina/emails/verification_notify_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('userina/emails/verification_notify_message.txt',
                                   context)
        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        self.verification_notification_send = True
        self.save()

    def change_email(self, email):
        """ Changes the e-mail address for a user """
        # Email is temporary until verified
        self.temporary_email = email

        # New verification key
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.verification_key = sha_constructor(salt+self.user.username).hexdigest()
        self.verification_key_created = datetime.datetime.now()

        # Send email for verification
        self.send_verification_email(new_email=True)
        self.save()

    def get_mugshot_url(self):
        """
        Returns the image containing the mugshot for the user. This can either
        an uploaded image or a gravatar.

        The uploaded image has precedence above the avatar.

        """
        # First check for a mugshot and if any return that.
        if self.mugshot:
            return self.mugshot.url

        # Use Gravatar if the user wants to.
        if userina_settings.USERINA_MUGSHOT_GRAVATAR:
            return get_gravatar(self.user.email,
                                userina_settings.USERINA_MUGSHOT_SIZE,
                                userina_settings.USERINA_MUGSHOT_DEFAULT)

        # Gravatar not used, check for a default image.
        else:
            if userina_settings.USERINA_MUGSHOT_DEFAULT:
                return userina_settings.USERINA_MUGSHOT_DEFAULT
            else: return ''

User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
