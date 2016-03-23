"""
Django accounts management made easy.

"""
default_app_config = 'userena.apps.UserenaConfig'

VERSION = (2, 0, 1)

__version__ = '.'.join((str(each) for each in VERSION[:4]))


def get_version():
    """
    Returns string with digit parts only as version.

    """
    return '.'.join((str(each) for each in VERSION[:3]))
