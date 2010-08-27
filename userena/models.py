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
from userena.managers import UserenaUserManager, UserenaBaseProfileManager
from userena import settings as userena_settings

from guardian.shortcuts import get_perms
from guardian.shortcuts import assign

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

class UserenaUser(User):
    """
    A user which stores all the nescessary information to have a full
    functional user implementation on your Django website.

    """
    user = models.OneToOneField(User,
                                verbose_name=_('user'),
                                parent_link=True)

    last_active = models.DateTimeField(null=True, blank=True)

    activation_key = models.CharField(_('activation key'), max_length=40,
                                        blank=True)
    activation_key_created = models.DateTimeField(_('creation date of activation key'),
                                                  blank=True,
                                                  null=True)
    activation_notification_send = models.BooleanField(_('notification send'),
                                                       default=False,
                                                       help_text=_('Designates whether this user has already got a notification about activating their account.'))

    email_new = models.EmailField(_('new wanted e-mail'),
                                  blank=True,
                                  help_text=_('Temporary email address when the user requests an email change.'))
    email_verification_key = models.CharField(_('new email verification key'),
                                              max_length=40,
                                              blank=True)

    objects = UserenaUserManager()

    @models.permalink
    def get_absolute_url(self):
        return ('userena_profile_detail', (), {'username': self.username})

    def change_email(self, email):
        """
        Changes the e-mail address for a user.

        A user needs to verify this new e-mail address before it becomes
        active. By storing the new e-mail address in a temporary field --
        ``temporary_email`` -- we are able to set this e-mail address after the
        user has verified it by clicking on the verfication URI in the email.
        This email get's send out by ``send_verification_email``.

        **Arguments**

        ``email``
            The new email address that the user wants to use.

        """
        self.email_new = email

        salt, hash = generate_sha1(self.username)
        self.email_verification_key = hash
        self.save()

        # Send email for activation
        self.send_verification_email()

    def send_verification_email(self):
        """
        Sends an email to verify the new email address.

        This email contains the ``email_verification_key`` which is used to
        verify this new email address in ``UserenaUser.objects.verify_email``.

        """
        protocol = 'https' if userena_settings.USERENA_USE_HTTPS else 'http'
        context= {'user': self,
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
        Checks if activation key is expired.

        Returns ``True`` when the ``activation_key`` of the user is expired and
        ``False`` if the key is still valid.

        The key is expired when it's set to the value defined in
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

    def send_activation_email(self):
        """
        Sends a activation e-mail to the user.

        This e-mail is send when the user wants to activate their newly created
        user. Also checks if the protocol is secured by looking at
        ``USERENE_USE_HTTPS`` value.

        """
        protocol = 'https' if userena_settings.USERENA_USE_HTTPS else 'http'
        context= {'user': self,
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
                  [self.email,])

class UserenaBaseProfile(models.Model):
    """ Base model needed for extra profile functionality """
    PRIVACY_CHOICES = (
        ('open', _('Open')),
        ('registered', _('Registered')),
        ('closed', _('Closed')),
    )

    MUGSHOT_SETTINGS = {'size': (userena_settings.USERENA_MUGSHOT_SIZE,
                                 userena_settings.USERENA_MUGSHOT_SIZE),
                        'crop': 'smart'}

    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')

    mugshot = ThumbnailerImageField(_('mugshot'),
                                    blank=True,
                                    upload_to=upload_to_mugshot,
                                    resize_source=MUGSHOT_SETTINGS,
                                    help_text=_('A personal image displayed in your profile.'))

    privacy = models.CharField(_('privacy'),
                               max_length=15,
                               choices=PRIVACY_CHOICES,
                               default='registered',
                               help_text = _('Designates who can view your profile.'))

    objects = UserenaBaseProfileManager()


    class Meta:
        """
        Meta options making the model abstract and defining permissions.

        The model is ``abstract`` because it only supplies basic functionality
        to a more custom defined model that extends it. This way there is not
        another join needed.

        We also define custom permissions because we don't know how the model
        that extends this one is going to be called. So we don't know what
        permissions to check. For ex. if the user defines a profile model that
        is called ``MyProfile``, than the permissions would be
        ``add_myprofile`` etc. We want to be able to always check
        ``add_profile``, ``change_profile`` etc.

        """
        abstract = True
        permissions = (
            ('add_profile', 'Can add profile'),
            ('change_profile', 'Can change profile'),
            ('delete_profile', 'Can delete profile'),
            ('view_profile', 'Can view profile'),
        )

    def get_mugshot_url(self):
        """
        Returns the image containing the mugshot for the user.

        The mugshot can be a uploaded image or a Gravatar.

        Gravatar functionality will only be used when
        ``USERENA_MUGSHOT_GRAVATAR`` is set to ``True``.

        Returns ``None`` when Gravatar is not used and no default image is
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

    def can_view_profile(self, user):
        """
        Can the ``user`` view this profile?

        Returns a boolean if a user has the rights to view the profile of this
        user.

        Users are divided into four groups:

            - Open: Everyone can view your profile
            - Closed: Nobody can view your profile.
            - Registered: Users that are registered on the website and signed
            in only.
            - Special cases like superadmin and the owner of the profile.

        Through the ``privacy`` field a owner of an profile can define what
        they want to show to whom.

        **Arguments**

        ``user``

            A django ``User`` instance.

        """
        # Simple cases first, we don't want to waste CPU and DB hits.
        # Everyone.
        if self.privacy == 'open': return True
        # Registered users.
        elif self.privacy == 'registered' and (isinstance(user, UserenaUser) or \
                                               isinstance(user, User)):
            return True

        # Checks done by guardian for owner and admins.
        elif 'view_profile' in get_perms(user, self):
            return True

        # Fallback to closed profile.
        return False

class UserenaProfile(UserenaBaseProfile):
    """ Default profile """
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
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
            # leap year
            try:
                birthday = self.birth_date.replace(year=today.year)
            except ValueError:
                birthday = self.birth_date.replace(year=today.year, day=today.day-1)
            if birthday > today: return today.year - self.birth_date.year - 1
            else: return today.year - self.birth_date.year
