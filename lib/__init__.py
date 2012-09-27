import datetime
import logging as log
import os
import pickle
import socket
import sys
import time
import traceback

class plugin:
    def __init__(self, conf):
        self.conf = conf
        self.data = {}

        data_file = '%s/%s.dat' % (conf['persist_dir'], conf['plugin_name'])
        log.debug('loading timestamp from %s', data_file)

        code_date = os.stat(sys.modules[self.__class__.__module__].__file__).st_mtime
        threshold = time.time() - int(conf['period']) * 60
        run_limit = max(code_date, threshold)

        log.debug('%s run limit: %s', conf['plugin_name'], datetime.datetime.fromtimestamp(run_limit))
        if not os.path.exists(data_file) or os.stat(data_file).st_mtime < run_limit:
            try:
                self.prev = pickle.load(open(data_file))
            except:
                self.prev = {}

            self.collect()
            self.publish()
            pickle.dump(self.data, open(data_file, 'w'))
        else:
            log.debug('%s: skipping run: recent change', data_file)

    def publish(self):
        m = []
        t = int(time.time())

        for k, v in self.data.items():
            if self.conf.get('only_deltas'):
                v = v - self.prev.get(k, 0)
            m.append('%s.%s.%s %s %d\r\n' % (self.conf['host_prefix'], self.conf['plugin_name'], k, v, t))

        s = mk_sock(self.conf['carbon_host'], self.conf['carbon_port'])
        s.send(''.join(m))

    def escape(self, label):
        quote = lambda t: t.replace('.', '$').replace('/', '^').replace(' ', '_')

        if type(label) in (list, tuple):
            return '.'.join([quote(i) for i in label if i])
        else:
            return quote(label)


def mk_sock(host, port=2004, cache={}):
    sock = socket.socket()
    name = '%s:%d' % (host, port)

    if name not in cache:
        sock.connect((host, port))
        cache[name] = sock

    return cache[name]

def log_exc(e, msg=None):
    if msg:
        log.error('%s: %s', msg, e)
    else:
        log.error(e)
    for line in traceback.format_exc().split('\n'):
        log.debug('  %s', line)
