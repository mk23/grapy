import grapy
import netsnmp
import re

class snmp_table (grapy.plugin):
    def collect(self):
        oid = netsnmp.VarList(netsnmp.Varbind(self.conf['poller_conf']['table']))
        netsnmp.snmpwalk(oid, DestHost=self.conf['hostname'], Version=self.conf['snmp_version'], Community=self.conf['snmp_community'], UseNumeric=True)

        tbl = {}
        for ret in oid:
            if ret.iid not in tbl:
                tbl[ret.iid] = {}

            tbl[ret.iid][ret.tag.split('.')[-1]] = ret.val
        tbl = sorted(tbl.items())

        for idx in xrange(len(tbl)):
            key, val = tbl[idx]
            for obj in self.conf['items']:
                skp = False
                for flt in obj.get('filter', ':'):
                    chk = flt.strip().split(':', 1)
                    skp = skp or not re.match(chk[1], val.get(chk[0], ''))

                if skp:
                    continue

                lbl = [val[i] if unicode(i).isnumeric() else i.format(index=idx, label=key) for i in obj['labels'].split('.')]
                self.data[self.escape(lbl)] = val[obj['values']]
