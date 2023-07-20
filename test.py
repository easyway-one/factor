#!/usr/bin/env python3
a = {}
b = {}

c = "aaa"
a[c] = True
c = "bbb"
a[c] = True
c = "ccc"
a[c] = True

c = "bbb"
b[c] = False
c = "ccc"
b[c] = False
c = "ddd"
b[c] = True

a.update(b)

print(a)

