import grapy
import socket

class memcached_stats(grapy.plugin):
    def collect(self):
        skip = [
            'pid',
            'uptime',
            'time',
            'version',
            'libevent',
            'pointer_size',
            'rusage_user',
            'rusage_system'
        ] + self.conf['skip']

        sock = socket.socket()
        sock.connect((self.conf['hostname'], self.conf.get('port', 11211)))

        sock.send('stats\r\n')

        buff = ''
        while True:
            buff += sock.recv(4096)
            if buff.endswith('END\r\n'):
                sock.send('quit\r\n')
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                break

        for line in buff.split('\r\n'):
            if line.startswith('STAT'):
                key, val = line.strip().split()[1:]
                if key not in skip:
                    self.data[key] = val
