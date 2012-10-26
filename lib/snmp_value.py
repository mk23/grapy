import grapy
import netsnmp

class snmp_value(grapy.plugin):
    def collect(self):
        for obj in self.conf['items']:
            oid = netsnmp.Varbind(obj['value'])
            netsnmp.snmpget(oid, DestHost=self.conf['hostname'], Version=self.conf['snmp_version'], Community=self.conf['snmp_community'], UseNumeric=True)

            self.data[self.escape(obj['label'])] = oid.val
