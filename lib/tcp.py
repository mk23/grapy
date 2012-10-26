import grapy
import socket

class tcp(grapy.plugin):
    def collect(self):
        conf = self.conf['poller_conf']
        sock = socket.socket()

        sock.connect((self.conf['hostname'], conf['port']))

        buff = ''
        if conf.get('wait') is not None:
            while True:
                buff += sock.recv(4096)
                find  = buff.find(conf['wait'])

                if find >= 0:
                    buff = buff[find:]
                    break

        if conf.get('send') is not None:
            sock.send(conf['send'])

        while True:
            buff += sock.recv(4096)
            if conf.get('last') is not None:
                find  = buff.find(conf['last'])

                if find >= 0:
                    buff = buff[:find]

                    if conf.get('quit') is not None:
                        sock.send(conf['quit'])

                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    break

        data = buff.split(conf['line']) if conf.get('line') is not None else buff
        self.parser(data)
