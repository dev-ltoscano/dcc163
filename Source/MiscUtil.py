# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt

def range_exclusive(start, end, increment=1):
    return range(start, end, increment)

def range_inclusive(start, end, increment=1):
    return range(start, end + 1, increment)

def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)