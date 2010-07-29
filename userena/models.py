from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.utils.hashcompat import sha_constructor

from userena.utils import get_gravatar
from userena.managers import AccountManager
from userena import settings as userena_settings

from dateutil.relativedelta import relativedelta
from easy_thumbnails.fields import ThumbnailerImageField

import datetime, random

def upload_to_mugshot(instance, filename):
    """
    Uploads a mugshot for a user to the ``USERENA_MUGSHOT_PATH`` and creating a
    unique hash for the image. This is for privacy reasons so others can't just
    browse through the mugshot directory.

    """
    extension = filename.split('.')[-1].lower()
    salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+str(instance.user.id)).hexdigest()[:10]
    return '%(path)s%(hash)s.%(extension)s' % {'path': userena_settings.USERENA_MUGSHOT_PATH,
                                               'hash': hash,
                                               'extension': extension}

class BaseAccount(models.Model):
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

    # Fields used for managing accounts
    last_active = models.DateTimeField(null=True, blank=True)

    activation_key = models.CharField(_('activation key'), max_length=40,
                                        blank=True)
    activation_key_created = models.DateTimeField(_('creation date of activation key'),
                                                  blank=True,
                                                  null=True)
    activation_notification_send = models.BooleanField(_('notification send'),
                                                       default=False,
                                                       help_text=_('Designates whether this user has already got a notification about activating their account.'))

    # To change their e-mail address, they first have to verify it.
    temporary_email = models.EmailField(_('temporary email'),
                                        blank=True,
                                        help_text=_('Temporary email address when the user requests an email change.'))

    objects = AccountManager()

    class Meta:
        if userena_settings.USERENA_CHILD_MODEL:
            abstract = True

    def __unicode__(self):
        return '%s' % self.user

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

    @property
    def get_activation_url(self):
        """ Simplify it to get the activation URI """
        site = Site.objects.get_current()
        path = reverse('userena_activate',
                       kwargs={'activation_key': self.activation_key})
        return 'http://%(domain)s%(path)s' % {'domain': site.domain,
                                              'path': path}

    def change_email(self, email):
        """
        Changes the e-mail address for a user.

        A user needs to verify this new e-mail address before it becomes
        active. By storing there new e-mail address in a temporary field --
        ``temporary_email`` -- we are able to set this e-mail address after the
        user has verified it by clicking on the activation URI in the
        activation e-mail. This e-mail get's send by
        ``send_activation_email``.

        """
        # Email is temporary until verified
        self.temporary_email = email

        # New activation key
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.activation_key = sha_constructor(salt+self.user.username).hexdigest()
        self.activation_key_created = datetime.datetime.now()

        # Send email for activation
        self.send_activation_email(new_email=True)
        self.save()

    def activation_key_expired(self):
        """
        Returns ``True`` when the ``activation_key`` of the account is
        expired and ``False`` if the key is still valid.

        The key is either expired when the key is set to the value defined in
        ``USERENA_ACTIVATED`` or ``activation_key_created`` is beyond the
        amount of days defined in ``USERENA_ACTIVATION_DAYS``.

        """
        expiration_days = datetime.timedelta(days=userena_settings.USERENA_ACTIVATION_DAYS)
        if self.activation_key == userena_settings.USERENA_ACTIVATED:
            return True
        if datetime.datetime.now() >= self.activation_key_created + expiration_days:
            return True
        return False

    def activation_key_almost_expired(self):
        """
        Returns ``True`` when the ``activation_key`` is almost expired.

        A key is almost expired when the there are less than
        ``USERENA_ACTIVATION_NOTIFY_DAYS`` days left before expiration.

        """
        notification_days = datetime.timedelta(days=(userena_settings.USERENA_ACTIVATION_DAYS - userena_settings.USERENA_ACTIVATION_NOTIFY_DAYS))
        if datetime.datetime.now() >= self.activation_key_created + notification_days:
            return True
        return False

    def send_activation_email(self):
        """
        Sends a activation e-mail to the user.

        This e-mail is send when the user wants to activate their newly created
        account.

        """
        context= {'account': self,
                  'activation_days': userena_settings.USERENA_ACTIVATION_DAYS,
                  'site': Site.objects.get_current()}

        subject = render_to_string('userena/emails/activation_email_subject.txt', context)
        subject = ''.join(subject.splitlines())

        message = render_to_string('userena/emails/activation_email_message.txt', context)
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

        # Gravatar not used, check for a default image. Don't use the gravatar defaults
        else:
            if userena_settings.USERENA_MUGSHOT_DEFAULT not in ['404', 'mm', 'identicon', 'monsterid', 'wavatar']:
                return userena_settings.USERENA_MUGSHOT_DEFAULT
            else: return None

def get_account_model():
    """
    Returns the right account model so your user application can be easily
    extended without adding extra relationships.

    """
    from django.db.models import get_model
    if userena_settings.USERENA_CHILD_MODEL:
        account_model = get_model(*userena_settings.USERENA_CHILD_MODEL.split('.', 2))
        if not account_model:
            raise ImproperlyConfigured('Cannot find the model defined in ``USERINA_CHILD_MODEL``.')
        return account_model

    return BaseAccount

# Return the model that's used for account functionality
Account = get_account_model()

# Always return an account when asked through a user
User.account = property(lambda u: Account.objects.get_or_create(user=u)[0])
