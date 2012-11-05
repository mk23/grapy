import datetime
import json
import logging as log
import os
import pickle
import re
import signal
import socket
import struct
import sys
import time
import traceback
import urllib2

class plugin:
    def __init__(self, conf):
        self.conf = conf
        self.data = {}

        data_file = '%s/%s.dat' % (conf['persist_dir'], conf['plugin_name'])
        log.debug('loading timestamp from %s', data_file)

        code_date = os.stat(sys.modules[self.__class__.__module__].__file__).st_mtime
        threshold = time.time() - int(conf['period']) * 60
        run_limit = max(code_date, threshold)

        signal.signal(signal.SIGALRM, self.timeout)

        log.debug('%s run limit: %s', conf['plugin_name'], datetime.datetime.fromtimestamp(run_limit))
        if not os.path.exists(data_file) or os.stat(data_file).st_mtime < run_limit:
            try:
                self.prev = pickle.load(open(data_file))
            except:
                self.prev = {}

            signal.alarm(self.conf['timeout'])
            self.collect()
            signal.alarm(0)

            prepare(dict(('%s.%s.%s' % (conf['host_prefix'], conf['plugin_name'], k), v) for k, v in self.data.items()))
            pickle.dump(self.data, open(data_file, 'w'))
        else:
            log.info('%s: skipping run: recent change', data_file)

    def timeout(self, *args):
        raise Exception('poller timed out (%ds)' % self.conf['timeout'])

    def escape(self, label):
        quote = lambda t: t.replace('.', '$').replace('/', '^').replace(' ', '_')

        if type(label) in (list, tuple):
            return '.'.join([quote(i) for i in label if i])
        else:
            return quote(label)

    def lookup(self, data, label, parts, key=None, val=None):
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
                    indx, patt = (urllib2.unquote(s) for s in indx.split('|'))
                    find = re.match('^%s$' % patt, data[indx])
                    if find:
                        key.extend(find.groups())
                        undo_one += len(find.groups())
                    else:
                        raise ValueError('^%s$: no match in: %s' % (patt, data[indx]))
                else:
                    key.append(data[urllib2.unquote(indx)])
                    undo_one += 1

            if part == '**':
                for atom in data:
                    self.lookup(atom, label, parts, key, val)

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
                            self.lookup(data[atom], label, parts, key, val)
                        else:
                            val[label.format(name=self.escape(key) if key else atom)] = data[atom]

                        for i in xrange(undo_two):
                            undo_two -= 1
                            key.pop()
        finally:
            for i in xrange(undo_one + undo_two):
                key.pop()

            return val

    def parser(self, text):
        data = getattr(self, 'parse_%s' % self.conf['parser'])(text)
        for item in self.conf['items']:
            label = item.get('label', '{name}')
            parts = item['value'].lstrip('/').split('/')
            for key, val in self.lookup(data, label, parts).items():
                self.data[key] = val

    def parse_json(self, data):
        return json.loads(data.read())

    def parse_text(self, data):
        value = re.compile(self.conf['parser_conf']['value'])
        parts = [re.compile(item) for item in self.conf['parser_conf'].get('parts', [])]

        items = {}
        stack = [items]
        for line in data:
            match = value.search(line)
            if match:
                stack[-1][match.group('label')] = match.group('value')
                continue

            for i in xrange(len(stack) - 1, 0, -1):
                if i == len(parts):
                    stack.pop()
                else:
                    match = parts[i].match(line)
                    if match:
                        label = match.group(1)
                        stack[-1][label] = {}
                        stack.append(stack[-1][label])
                        break
                    else:
                        stack.pop()
            else:
                if len(parts) < len(stack):
                    continue

                match = parts[len(stack) - 1].match(line)
                if match:
                    label = match.group(1)
                    stack[-1][label] = {}
                    stack.append(stack[-1][label])

        return items

def prepare(data=None, test=False, cache={}):
    if type(data) == dict:
        cache.update(data)
    return cache if not test else len(cache) > 0

def publish(host, port, proto='text'):
    if not prepare(test=True):
        log.info('skipping empty publish')
        return

    t = int(time.time())
    s = socket.socket()

    if proto == 'text':
        m = ''.join('%s %s %d\n' % (k, v, t) for k, v in sorted(prepare().items()))
    elif proto == 'pickle':
        p = pickle.dumps([(k, (t, v)) for k, v in sorted(prepare().items())])
        m = struct.pack('!L', len(p)) + p

    s.connect((host, port))
    s.send(m)

def log_exc(e, msg=None):
    if msg:
        log.error('%s: %s', msg, e)
    else:
        log.error(e)
    for line in traceback.format_exc().split('\n'):
        log.debug('  %s', line)
