#!/usr/bin/env python

import shelve

d1 = { 'int': 10, 'float':9.5, 'string':'Sample data' }
d2 = { 'int': 13, 'dict' : d1}

s = shelve.open('test_shelf.db')
try:
    s['key1'] = d2
finally:
    s.close()
