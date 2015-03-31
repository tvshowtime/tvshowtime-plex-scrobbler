import urllib2
import urllib
import urlparse
import xml.etree.ElementTree
import re
from htmlentitydefs import name2codepoint
import hashlib
import sys
import logging
import time
import os
import json


class Tvst(object):

    CLIENT_ID = 'va0D2CEfSPNNlLoYMYYT'
    CLIENT_SECRET = 'RF51gSEZBJAbLXmEUCZ8thJAwJPAyQSafCQCyqOt'
    USER_AGENT = 'plex-tvst-scrobbler'

    def __init__(self, cfg):

        self.logger = logging.getLogger(__name__)
        self.cfg = cfg

    def get_session(self):

        if os.path.exists(self.cfg.get('plex-tvst-scrobbler', 'session')):
            sessfp = open(self.cfg.get('plex-tvst-scrobbler', 'session'), 'r')
            session = sessfp.read().strip()
            sessfp.close()
        return session


    def _do_tvst_post(self, url, data):

        f = urllib2.Request(url)
        f.add_header('User-Agent', self.USER_AGENT)
        try:
            res = urllib2.urlopen(f, data)
            return json.load(res)
        except urllib2.URLError, e:
            self.logger.error('Unable to submit post data {url} - {error}'.format(
                url=url, error=e))
            raise

    def _get_auth_infos(self):
        args = {
            'client_id': self.CLIENT_ID
        }

        url = urlparse.urlunparse(('https',
                                  'api.tvshowtime.com',
                                  '/v1/oauth/device/code', '', '', ''))

        res = self._do_tvst_post(url, urllib.urlencode(args))

        return res

    def _get_access_token(self, code):
        args = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'code': code,
        }
        url = urlparse.urlunparse(('https',
                                  'api.tvshowtime.com',
                                  '/v1/oauth/access_token', '', '', ''))
        res = self._do_tvst_post(url, urllib.urlencode(args))

        return res

    def scrobble(self, show_id, season_number, number):

        session = self.get_session()
        self.logger.info(u'submitting {show_id} - S{season_number}E{number} to tvshowtime.com.'.format(
                show_id=show_id, season_number=season_number.zfill(2), number=number.zfill(2)))

        args = {
            'access_token': session,
            'show_id': show_id,
            'season_number': season_number.zfill(2),
            'number': number.zfill(2)
        }
        url = urlparse.urlunparse(('https',
                                  'api.tvshowtime.com',
                                  '/v1/checkin', '', '', ''))

        try:
            res = self._do_tvst_post(url, urllib.urlencode(args))
        except:
            return False

        return True

    def tvst_auth(self):

        print '== Requesting tvshowtime.com auth =='

        auth_infos = self._get_auth_infos()
        accepted = 'n'

        print '\nPlease do the following to authorize the scrobbler:\n\n1/ Connect on {auth_url}\n2/ Enter the code: {code}'.format(
                auth_url=auth_infos['verification_url'], code=auth_infos['user_code'])
        while accepted.lower() == 'n':
            print
            accepted = raw_input('Have you authorized me [y/N] :')

        try:
            access_token_infos = self._get_access_token(auth_infos['device_code'])
        except urllib2.HTTPError, e:
            self.logger.error('Unable to send authorization request {error}'.format(error=e))
            return False

        if access_token_infos['result'] != 'OK':
            print access_token_infos['message']
            return


        token = access_token_infos['access_token']

        fp = open(self.cfg.get('plex-tvst-scrobbler', 'session'), 'w')
        fp.write(token)
        fp.close()
        self.logger.info('TVShow Time authorization successful.')
