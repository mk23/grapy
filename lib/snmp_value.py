import grapy
import netsnmp

class snmp_value(grapy.plugin):
    def collect(self):
        for obj in self.conf['objects'].values():
            oid = netsnmp.Varbind(obj['value'])
            netsnmp.snmpget(oid, DestHost=self.conf['hostname'], Version=self.conf['snmp_ver'], Community=self.conf['snmp_com'], UseNumeric=True)

            self.data[self.escape(obj['label'])] = oid.val
