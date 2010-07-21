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
    Uploads a mugshot for a user to the ``USERINA_MUGSHOT_PATH`` and creating a
    unique hash for the image. This is for privacy reasons so others can't just
    browse through the mugshot directory.

    """
    extension = filename.split('.')[-1]
    salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+str(instance.user.id)).hexdigest()[:10]
    return '%(path)s%(hash)s.%(extension)s' % {'path': userina_settings.USERINA_MUGSHOT_PATH,
                                               'hash': hash,
                                               'extension': extension}

class AccountManager(models.Manager):
    """ Extra functionality for the account manager. """
    def create_user(self, username, email, password):
        """
        A simple wrapper that creates a new ``User`` and a new ``Account``.

        """
        new_user = User.objects.create_user(username, email, password)
        new_user.save()

        account = self.create_account(new_user)
        return new_user

    def create_account(self, user):
        """
        Create an ``Account`` for a given ``User``.

        Also creates a ``verification_key`` for this account. After the account
        is created an e-mail is send with ``send_verification_email`` to the
        user with this key.

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
        Verify an ``Account`` by supplying a valid ``verification_key``.

        If the key is valid and an account is found, verify the account and
        return the verified account. But not before checking if the
        verification is for a _new_ account or a _updated_ account.

        A new account is when a user signed up and tries to verify the account.
        Only ``is_verified`` should be set to ``True``.

        If a user wants to change their e-mail address they also need to verify
        it. You could say that ``verify_account`` is then a verify_email. When
        this is the case, after successfull verification, the users e-mail
        address should be set to the ``temporary_email``.

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
        expiration. For each account that's found ``send_expiry_notification``
        is called.

        Returns a list of all the accounts that have received a notification.

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
        it. Skips if the user ``is_staff``.

        Returns a list of the deleted accounts.

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
                                    resize_source=MUGSHOT_SETTINGS,
                                    help_text=(_('A personal image displayed in your profile.'))
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)
    location =  models.CharField(_('location'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)

    # Fields used for managing accounts
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

    @models.permalink
    def get_absolute_url(self):
        return ('userina_me', ())

    @property
    def activity(self):
        """
        Returning the activity of the user

        @TIP: http://www.arnebrodowski.de/blog/482-Tracking-user-activity-with-Django.html

        """
        pass

    @property
    def age(self):
        """ Returns integer telling the age in years for the user """
        today = datetime.date.today()
        return relativedelta(today, self.birth_date).years

    def change_email(self, email):
        """
        Changes the e-mail address for a user.

        A user needs to verify this new e-mail address before it becomes
        active. By storing there new e-mail address in a temporary field --
        ``temporary_email`` -- we are able to set this e-mail address after the
        user has verified it by clicking on the verification URI in the
        verification e-mail. This e-mail get's send by
        ``send_verification_email``.

        """
        # Email is temporary until verified
        self.temporary_email = email

        # New verification key
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.verification_key = sha_constructor(salt+self.user.username).hexdigest()
        self.verification_key_created = datetime.datetime.now()

        # Send email for verification
        self.send_verification_email(new_email=True)
        self.save()

    @property
    def get_verification_url(self):
        """ Simplify it to get the verification URI """
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

        A key is almost expired when the there are less than
        ``USERINA_VERIFICATION_NOTIFY_DAYS`` days left before expiration.

        """
        notification_days = datetime.timedelta(days=(userina_settings.USERINA_VERIFICATION_DAYS - userina_settings.USERINA_VERIFICATION_NOTIFY_DAYS))
        if datetime.datetime.now() >= self.verification_key_created + notification_days:
            return True
        return False

    def send_verification_email(self, new_email=False):
        """
        Sends a verification e-mail to the user.

        This e-mail is either when the user wants to verify his newly created
        account or when the user changed their e-mail address.

        If ``new_email`` is set to ``True`` than the user will get an
        verification email address to his ``temporary_email`` address. This way
        they can verify their new e-mail address.

        """
        # Which templates to use, either for a new account, or for a e-mail
        # address change.
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
        """
        Notify the user that his account is about to expire.

        Sends an e-mail to the user telling them that their account is
        ``USERINA_VERIFICATION_NOTIFY_DAYS`` away before expiring.

        """
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

    def get_mugshot_url(self):
        """
        Returns the image containing the mugshot for the user. This can either
        an uploaded image or a Gravatar.

        Gravatar functionality will only be used when
        ``USERINA_MUGSHOT_GRAVATAR`` is set to ``True``.

        Return ``None`` when Gravatar is not used and no default image is
        supplied by ``USERINA_MUGSHOT_DEFAULT``.

        """
        # First check for a mugshot and if any return that.
        if self.mugshot:
            return self.mugshot.url

        # Use Gravatar if the user wants to.
        if userina_settings.USERINA_MUGSHOT_GRAVATAR:
            return get_gravatar(self.user.email,
                                userina_settings.USERINA_MUGSHOT_SIZE,
                                userina_settings.USERINA_MUGSHOT_DEFAULT)

        # Gravatar not used, check for a default image. Don't use the gravatar defaults
        else:
            if userina_settings.USERINA_MUGSHOT_DEFAULT not in ['404', 'mm', 'identicon', 'monsterid', 'wavatar']:
                return userina_settings.USERINA_MUGSHOT_DEFAULT
            else: return None

User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
