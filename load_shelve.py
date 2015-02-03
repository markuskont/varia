#!/usr/bin/env python

import shelve

s = shelve.open('/tmp/diff.db')
try:
    existing = s['key1']
finally:
    s.close()

print existing
