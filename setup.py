import os
from distutils.core import setup

NAME = 'plex-tvst-scrobbler'
VERSION = '1.3.1'

setup(
    name = 'plex_tvst_scrobbler',
    version = VERSION,
    author = 'Jesse Ward',
    author_email = 'team@tvshowtime.com',
    description = ('Scrobble TV shows played via Plex Media Center'),
    license = 'MIT',
    url = 'https://github.com/tvshowtime/plex-tvst-scrobbler',
    scripts = ['scripts/plex-tvst-scrobbler.py'],
    packages=['plex_tvst_scrobbler'],
    data_files = [(
      os.path.expanduser('~/.config/{0}'.format(NAME)),
      ['conf/plex_tvst_scrobbler.conf'],
      )]
)
