#!/usr/bin/env python

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

    for line in stats.split("\n"):
        data = re.match('\s+(\w+): (\d+)', line)
        if not data: 
            continue
        name = data.group(1)
        value = data.group(2)
        oid = gen_oid(name)
        #pp.add_cnt_64bit(oid, value)

def main():
    update()

if __name__ == "__main__":
    main()
