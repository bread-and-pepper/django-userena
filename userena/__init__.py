"""
Implementation of per object permissions for Django 1.2.
"""
VERSION = (0, 1, 1, 'dev')

__version__ = '.'.join((str(each) for each in VERSION[:4]))

def get_version():
    """
    Returns string with digit parts only as version.

    """
    return '.'.join((str(each) for each in VERSION[:3]))
