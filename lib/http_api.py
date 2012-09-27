import grapy
import json
import re
import urllib2

class http_api(grapy.plugin):
    def collect(self):
        api_url = '{scheme}://{hostname}:{port}{path}'.format(**self.conf)
        if self.conf.get('auth_type') in ('basic', 'digest'):
            pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            pass_mgr.add_password(user=self.conf['auth_user'], passwd=self.conf['auth_pass'], uri=api_url, realm=None)
            auth_hdl = getattr(urllib2, 'HTTP%sAuthHandler' % self.conf['auth_type'].title())(pass_mgr)
            urllib2.install_opener(urllib2.build_opener(auth_hdl))

        getattr(self, '%s_parser' % self.conf['parser'])(urllib2.urlopen(api_url).read())

    def regex_parser(self, text):
        for item in self.conf['items']:
            find = re.search(item['regex'], text)
            if find and len(find.groups()):
                key = item.get('value', '').split('.') + [find.groupdict().get('label')]
                val = find.groupdict().get('value', find.group(0))

                self.data[self.escape(key)] = val



    def json_parser(self, text):
        data = json.loads(text)
        for item in self.conf['items']:
            label = item.get('label', '{name}')
            parts = item['value'].lstrip('/').split('/')
            for key, val in self.json_lookup(data, label, parts).items():
                self.data[key] = val


    def json_lookup(self, data, label, parts, key=None, val=None):
        if key is None:
            key = []
        if val is None:
            val = {}

        undo_one = undo_two = 0
        try:
            part, parts = parts[0], parts[1:]
            if ':' in part:
                indx, part = part.split(':')
                if '|' in indx:
                    indx, patt = indx.split('|')
                    find = re.match('^%s$' % urllib2.unquote(patt), data[urllib2.unquote(indx)])
                    if find:
                        key.extend(find.groups())
                        undo_one += len(find.groups())
                    else:
                        raise ValueError('%s: no match' % patt)
                else:
                    key.append(data[urllib2.unquote(indx)])
                    undo_one += 1

            if part == '**':
                for atom in data:
                    self.json_lookup(atom, label, parts, key, val)

                for i in xrange(undo_one):
                    undo_one -= 1
                    key.pop()
            else:
                for atom in data:
                    find = re.match('^%s$' % urllib2.unquote(part), atom)
                    if find:
                        key.extend(find.groups())
                        undo_two += len(find.groups())

                        if len(parts) > 0:
                            self.json_lookup(data[atom], label, parts, key, val)
                        else:
                            val[label.format(name=self.escape(key) if key else atom)] = data[atom]

                        for i in xrange(undo_two):
                            undo_two -= 1
                            key.pop()
        finally:
            for i in xrange(undo_one + undo_two):
                key.pop()

        return val
