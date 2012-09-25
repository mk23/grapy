import grapy

class example_module(grapy.plugin):
    def collect(self):
        for item in self.conf['objects'].values():
            self.data[item['item']] = self.prev.get(item['item'], 0) + 1
