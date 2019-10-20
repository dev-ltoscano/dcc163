# -*- coding: utf-8 -*-
def range_exclusive(start, end, increment=1):
    return range(start, end, increment)

def range_inclusive(start, end, increment=1):
    return range(start, end + 1, increment)