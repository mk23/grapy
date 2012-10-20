import grapy
import urllib2

class http(grapy.plugin):
    def collect(self):
        url = '{scheme}://{hostname}:{port}{path}'.format(**self.conf)
        if self.conf.get('auth_type') in ('basic', 'digest'):
            mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            mgr.add_password(user=self.conf['auth_user'], passwd=self.conf['auth_pass'], uri=url, realm=None)
            hdl = getattr(urllib2, 'HTTP%sAuthHandler' % self.conf['auth_type'].title())(mgr)
            urllib2.install_opener(urllib2.build_opener(hdl))

        self.parser(urllib2.urlopen(url))
