#!/usr/bin/env python

import shelve

s = shelve.open('/tmp/test.db')
try:
    raw = s['key1']
finally:
    s.close()

s = shelve.open('/tmp/diff.db')
try:
    diff = s['key1']
finally:
    s.close()

print raw
print "---------------------------------"
print diff
