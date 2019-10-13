# -*- coding: utf-8 -*-
import math

def calculateDistanceBetweenGeoPoints(p1, p2):
    d2r = (math.pi / 180.0)
    
    diffLat = (p1.latitude - p2.latitude) * d2r
    diffLong = (p1.longitude - p2.longitude) * d2r
    
    a = pow(math.sin(diffLat / 2.0), 2) + math.cos(p1.latitude * d2r) * math.cos(p2.latitude * d2r) * pow(math.sin(diffLong / 2.0), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return 1000 * (6367 * c)

class HataSRDModel:
    def __init__(self):
        self.constant = 69.55
        self.baseStationHeight = 30.0
        self.mobileStationHeight = 1.5
        
    def getDistance(self, antenna, frequency, potency, signalLevel):
        bhb = (1.1 * math.log10(frequency) - 0.7) * min(10.0, self.baseStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.baseStationHeight / 10.0))
        ahm = (1.1 * math.log10(frequency) - 0.7) * min(10, self.mobileStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.mobileStationHeight / 10.0))
        hata = potency - signalLevel + antenna
        
        return 1000.0 * pow(10.0, (hata - self.constant - 26.16 * math.log10(frequency) + 13.82 * math.log10(self.baseStationHeight) + ahm + bhb) / (44.9 - 6.55 * math.log10(self.baseStationHeight)))
        