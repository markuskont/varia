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
        oid+= "." + str(ord(a))

    return oid

def update():

    stats=execute_command()
    # temp
    index=1

    for line in stats.split("\n"):
        data = re.match('\s+(\w+): (\d+)', line)
        if not data: 
            continue
        name = data.group(1)
        value = int(data.group(2))
        #oid = gen_oid(name)
        # temp
        oid = "%d.%s" % (index,
                 ".".join([str(ord(a)) for a in name]))
        pp.add_cnt_64bit(oid, value)

update()

pp = snmp.PassPersist('.1.3.6.1.4.1.39178.100.1.1.1.2')
pp.start(update, 10)
