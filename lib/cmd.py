import grapy
import shlex
import subprocess

class cmd(grapy.plugin):
    def collect(self):
        conf = self.conf['poller_conf']

        if type(conf['exec']) not in (list, tuple):
            conf['exec'] = [conf['exec']]
        if type(conf.get('code')) not in (list, tuple):
            conf['code'] = [conf.get('code', 0)]

        proc = None
        for line in conf['exec']:
            pipe = proc.stdout if proc else None
            proc = subprocess.Popen(shlex.split(line), stdin=pipe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = proc.communicate()
        if proc.returncode in conf['code']:
            data = out.split(conf.get('line', '\n'))
            self.parser(data)
        else:
            raise RuntimeError('command return bad exit status (%d)\n\n%s' % (proc.returncode, err.strip()))
