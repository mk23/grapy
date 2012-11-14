import grapy
import urllib2

class http(grapy.poller):
    def collect(self):
        cfg = self.conf['poller_conf']
        url = '{scheme}://{hostname}:{port}{path}'.format(hostname=self.conf['hostname'], **cfg)
        if self.conf['poller_conf'].get('auth', {}).get('type') in ('basic', 'digest'):
            mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            mgr.add_password(user=cfg['auth']['user'], passwd=cfg['auth']['pass'], uri=url, realm=None)
            hdl = getattr(urllib2, 'HTTP%sAuthHandler' % cfg['auth']['type'].title())(mgr)
            urllib2.install_opener(urllib2.build_opener(hdl))

        self.parser(urllib2.urlopen(url))
