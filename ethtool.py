#!/usr/bin/python -u

import sys, os, re

try:
    import snmp_passpersist as snmp
except:
    print "no snmp-passpersist module installed:"
    print "pip install snmp-passpersist"

def execute_command():
    cmd='ethtool -S wlan0'
    
    return os.popen(cmd).read()

def gen_oid(argv):

    oid=""    
    for a in argv:
        oid+= ".".join(str(ord(a)))

    return oid

def update():

    stats=execute_command()

    for line in stats.split("\n"):
        data = re.match('\s+(\w+): (\d+)', line)
        if not data: 
            continue
        name = data.group(1)
        value = int(data.group(2))
        oid = gen_oid(name)
        pp.add_cnt_64bit(oid, value)

pp = snmp.PassPersist('.1.3.6.1.4.1.39178.100.1.1.1.2')
pp.start(update, 10)
