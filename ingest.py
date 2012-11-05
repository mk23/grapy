#!/usr/bin/env python2.7

import datetime
import pickle
import struct
import sys

from gevent.server import StreamServer

def logger(msg, *args):
    print '[%s] %s' % (datetime.datetime.now(), msg % args)

def ingest_text(socket, remote):
    logger('conn: %s:%s', *remote)

    reader = socket.makefile()
    while True:
        line = reader.readline()
        if not line:
            logger('disc: %s:%s', *remote)
            break

        reader.flush()
        logger('read: %r', line)

def ingest_pickle(socket, remote):
    logger('conn: %s:%s', *remote)

    while True:
        head = struct.unpack('!L', socket.recv(4))[0]
        data = pickle.loads(socket.recv(head))

        logger('read: %d len payload', head)
        for item in data:
            logger('data: %s %s %d', item[0], item[1][1], item[1][0])

        break



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='carbon server simulator')
    parser.add_argument('-p', '--port', default=2003, type=int,
                        help='server port')
    parser.add_argument('-t', '--type', default='text', choices=['text', 'pickle'],
                        help='protocol type')
    args = parser.parse_args()

    logger('starting ingestion server on port 2004')
    server = StreamServer(('0.0.0.0', args.port), getattr(sys.modules[__name__], 'ingest_%s' % args.type))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print
        logger('exiting')
        sys.exit(0)
