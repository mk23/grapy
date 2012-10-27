import grapy

class file(grapy.plugin):
    def collect(self):
        self.parser(open(self.conf['poller_conf']['file']))
