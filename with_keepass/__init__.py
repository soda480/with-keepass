from os import getenv

if getenv('DEV'):
    version = '0.0.0-dev.1'
else:
    version = '1.0.2'

__version__ = version
