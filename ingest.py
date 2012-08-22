#!/usr/bin/env python2.7

import datetime, sys
from gevent.server import StreamServer

def logger(msg, *args):
    print '[%s] %s' % (datetime.datetime.now(), msg % args)

def ingest(socket, remote):
    logger('conn: %s:%s', *remote)

    reader = socket.makefile()
    while True:
        line = reader.readline()
        if not line:
            logger('disc: %s:%s', *remote)
            break

        reader.flush()
        logger('read: %r', line)


if __name__ == '__main__':
    logger('starting ingestion server on port 2004')

    server = StreamServer(('0.0.0.0', 2004), ingest)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print
        logger('exiting')
        sys.exit(0)
