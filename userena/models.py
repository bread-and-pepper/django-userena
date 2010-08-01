from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured

from userena.utils import get_gravatar, generate_sha1
from userena.managers import AccountManager
from userena import settings as userena_settings

from dateutil.relativedelta import relativedelta
from easy_thumbnails.fields import ThumbnailerImageField

import datetime, random

def upload_to_mugshot(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERENA_MUGSHOT_PATH`` and saving it
    under unique hash for the image. This is for privacy reasons so others
    can't just browse through the mugshot directory.

    """
    extension = filename.split('.')[-1].lower()
    salt, hash = generate_sha1(instance.id)
    return '%(path)s%(hash)s.%(extension)s' % {'path': userena_settings.USERENA_MUGSHOT_PATH,
                                               'hash': hash[:10],
                                               'extension': extension}

class Account(models.Model):
    """
    A user account which stores all the nescessary information to have a full
    functional user implementation on your Django website.

    """
    MUGSHOT_SETTINGS = {'size': (userena_settings.USERENA_MUGSHOT_SIZE,
                                 userena_settings.USERENA_MUGSHOT_SIZE),
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
                                    help_text=_('A personal image displayed in your profile.'))
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=True)
    location =  models.CharField(_('location'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)

    # Fields used for managment purposes.
    last_active = models.DateTimeField(null=True, blank=True)

    activation_key = models.CharField(_('activation key'), max_length=40,
                                        blank=True)
    activation_key_created = models.DateTimeField(_('creation date of activation key'),
                                                  blank=True,
                                                  null=True)
    activation_notification_send = models.BooleanField(_('notification send'),
                                                       default=False,
                                                       help_text=_('Designates whether this user has already got a notification about activating their account.'))

    # Email verification
    email_new = models.EmailField(_('new wanted e-mail'),
                                  blank=True,
                                  help_text=_('Temporary email address when the user requests an email change.'))
    email_verification_key = models.CharField(_('new email verification key'),
                                              max_length=40,
                                              blank=True)

    objects = AccountManager()

    def __unicode__(self):
        return '%s' % self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('userena_detail', (), {'username': self.user.username})

    @property
    def activity(self):
        """
        Returning the activity of the user.

        http://www.arnebrodowski.de/blog/482-Tracking-user-activity-with-Django.html

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
        user has verified it by clicking on the verfication URI in the email
        send by ``send_activation_email``.

        **Arguments**

        ``email``
            The new email address that the user wants to use.

        """
        self.email_new = email

        salt, hash = generate_sha1(self.user.username)
        self.email_verification_key = hash
        self.save()

        # Send email for activation
        self.send_verification_email()

    def send_verification_email(self):
        """
        Send email verification email. Strange, but correct sentence.

        Sends an email to verify a supplied email. This email contains the
        ``email_verification_key`` which is used to verify this new email
        address.

        """
        protocol = 'https' if userena_settings.USERENA_USE_HTTPS else 'http'
        context= {'account': self,
                  'protocol': protocol,
                  'verification_key': self.email_verification_key,
                  'site': Site.objects.get_current()}

        subject = render_to_string('userena/emails/verification_email_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('userena/emails/verification_email_message.txt',
                                   context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.email_new,])

    def activation_key_expired(self):
        """
        Returns ``True`` when the ``activation_key`` of the account is
        expired and ``False`` if the key is still valid.

        The key is either expired when the key is set to the value defined in
        ``USERENA_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``USERENA_ACTIVATION_DAYS``.

        """
        expiration_days = datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS)
        expiration_date = self.activation_key_created + expiration_days
        if self.activation_key == userena_settings.USERENA_ACTIVATED:
            return True
        if datetime.datetime.now() >= expiration_date:
            return True
        return False

    def activation_key_almost_expired(self):
        """
        Returns ``True`` when the ``activation_key`` is almost expired.

        A key is almost expired when the there are less than
        ``USERENA_ACTIVATION_NOTIFY_DAYS`` days left before expiration.

        """
        days = userena_settings.USERENA_ACTIVATION_DAYS - \
               userena_settings.USERENA_ACTIVATION_NOTIFY_DAYS
        notification_days = datetime.timedelta(days=days)

        notification_date = self.activation_key_created + notification_days
        if datetime.datetime.now() >= notification_date:
            return True
        return False

    def send_activation_email(self):
        """
        Sends a activation e-mail to the user.

        This e-mail is send when the user wants to activate their newly created
        account.

        """
        protocol = 'https' if userena_settings.USERENA_USE_HTTPS else 'http'
        context= {'account': self,
                  'protocol': protocol,
                  'activation_days': userena_settings.USERENA_ACTIVATION_DAYS,
                  'activation_key': self.activation_key,
                  'site': Site.objects.get_current()}

        subject = render_to_string('userena/emails/activation_email_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('userena/emails/activation_email_message.txt',
                                   context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email,])

    def send_expiry_notification(self):
        """
        Notify the user that his account is about to expire.

        Sends an e-mail to the user telling them that their account is
        ``USERENA_ACTIVATION_NOTIFY_DAYS`` away before expiring.

        """
        context = {'account': self,
                   'days_left': userena_settings.USERENA_ACTIVATION_NOTIFY_DAYS,
                   'site': Site.objects.get_current()}

        subject = render_to_string('userena/emails/activation_notify_subject.txt',
                                   context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('userena/emails/activation_notify_message.txt',
                                   context)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        self.activation_notification_send = True
        self.save()

    def get_mugshot_url(self):
        """
        Returns the image containing the mugshot for the user. This can either
        an uploaded image or a Gravatar.

        Gravatar functionality will only be used when
        ``USERENA_MUGSHOT_GRAVATAR`` is set to ``True``.

        Return ``None`` when Gravatar is not used and no default image is
        supplied by ``USERENA_MUGSHOT_DEFAULT``.

        """
        # First check for a mugshot and if any return that.
        if self.mugshot:
            return self.mugshot.url

        # Use Gravatar if the user wants to.
        if userena_settings.USERENA_MUGSHOT_GRAVATAR:
            return get_gravatar(self.user.email,
                                userena_settings.USERENA_MUGSHOT_SIZE,
                                userena_settings.USERENA_MUGSHOT_DEFAULT)

        # Gravatar not used, check for a default image.
        else:
            if userena_settings.USERENA_MUGSHOT_DEFAULT not in ['404', 'mm',
                                                                'identicon',
                                                                'monsterid',
                                                                'wavatar']:
                return userena_settings.USERENA_MUGSHOT_DEFAULT
            else: return None

# Always return an account when asked through a user
User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
