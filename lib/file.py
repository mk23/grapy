import grapy

class file(grapy.poller):
    def collect(self):
        self.parser(open(self.conf['poller_conf']['file']))
