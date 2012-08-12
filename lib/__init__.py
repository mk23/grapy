import datetime
import logging as log
import os
import sys
import time
import traceback

class plugin:
    def __init__(self, conf):
        self.conf = conf
        self.data = {}

        data_file = '%s/%s.dat' % (conf['ts_dir'], conf['name'])
        log.debug('loading time stamp from %s', data_file)

        threshold = time.time() - int(conf['interval'])
        code_date = os.stat(sys.modules[self.__class__.__module__].__file__).st_mtime
        run_limit = max(code_date, threshold)

        log.debug('%s run limit: %s', conf['name'], datetime.datetime.fromtimestamp(run_limit))
        if not os.path.exists(data_file) or os.stat(data_file).st_mtime < run_limit:
            self.gather()
            print self.data
        else:
            log.debug('%s: skipping run: recent change', data_file)

def log_exc(e, msg=None):
    if msg:
        log.error('%s: %s', msg, e)
    else:
        log.error(e)
    for line in traceback.format_exc().split('\n'):
        log.debug('  %s', line)
