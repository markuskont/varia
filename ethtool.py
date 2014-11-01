#!/usr/bin/env python

import sys, os, re

# Simply get all SMART data for device
def read_smart():
    cmd='ethtool -S wlan0'
    
    return os.popen(cmd).read()

# check if device is HDD or SSD

def main():
    stats=read_smart()

    print stats

if __name__ == "__main__":
    main()
