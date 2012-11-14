import grapy

class example(grapy.poller):
    def collect(self):
        for item in self.conf['objects'].values():
            self.data[item['item']] = self.prev.get(item['item'], 0) + 1
