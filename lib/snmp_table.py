import grapy
import netsnmp
import re

import pprint
class snmp_table (grapy.plugin):
    def gather(self):
        oid = netsnmp.VarList(netsnmp.Varbind(self.conf['table']))
        netsnmp.snmpwalk(oid, DestHost=self.conf['hostname'], Version=self.conf['snmp_ver'], Community=self.conf['snmp_com'], UseNumeric=True)

        tbl = {}
        for ret in oid:
            if ret.iid not in tbl:
                tbl[ret.iid] = {}

            tbl[ret.iid][ret.tag.split('.')[-1]] = ret.val
        tbl = sorted(tbl.items())

        for idx in xrange(len(tbl)):
            key, val = tbl[idx]
            for obj in self.conf['objects'].values():
                skp = False
                for flt in obj.get('filter', ':').strip().split('\n'):
                    chk = flt.strip().split(':', 1)
                    skp = skp or not re.match(chk[1], val.get(chk[0], ''))

                if skp:
                    continue

                lbl = [val[i] if unicode(i).isnumeric() else i.format(index=idx, label=key) for i in obj['labels'].split('.')]
                self.data['.'.join(lbl)] = val[obj['values']]

#        pprint.pprint(oid)
#        pprint.pprint(self.conf['objects'])

#        if unicode(self.conf['labels']).isnumeric():
#            for idx in xrange(len(oid)):
#                key = oid[idx].tag.strip('.')[-1]
#                self.data[self.conf['labels'].format(index=idx, token=key)] = oid[idx].val
#
#        print self.data
