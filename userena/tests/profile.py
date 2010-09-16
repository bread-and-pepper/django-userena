from userena.models import UserenaBaseProfile

class TestProfile(UserenaBaseProfile):
    """ A profile used for testing. """
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
    about_me = models.TextField(_('about me'), blank=True)
