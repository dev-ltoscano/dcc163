# -*- coding: utf-8 -*-
import math

def arc_to_deg(arc):
    """convert spherical arc length [m] to great circle distance [deg]"""
    return float(arc)/6371/1000 * 180/math.pi

def deg_to_arc(deg):
    """convert great circle distance [deg] to spherical arc length [m]"""
    return float(deg)*6371*1000 * math.pi/180

def latlon_to_xyz(lat, lon):
    """Convert angluar to cartesian coordiantes

    latitude is the 90deg - zenith angle in range [-90;90]
    lonitude is the azimuthal angle in range [-180;180] 
    """
    r = 6371 # https://en.wikipedia.org/wiki/Earth_radius
    theta = math.pi/2 - math.radians(lat) 
    phi = math.radians(lon)
    x = r * math.sin(theta) * math.cos(phi) # bronstein (3.381a)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    
    return [x,y,z]

def xyz_to_latlon (x,y,z):
    """Convert cartesian to angular lat/lon coordiantes"""
    r = math.sqrt(x**2 + y**2 + z**2)
    theta = math.asin(z/r) # https://stackoverflow.com/a/1185413/4933053
    phi = math.atan2(y,x)
    lat = math.degrees(theta)
    lon = math.degrees(phi)
    return [lat,lon]

def calculateDistanceBetweenGeoPoints(p1, p2):
    d2r = (math.pi / 180.0)
    
    diffLat = (p1.latitude - p2.latitude) * d2r
    diffLong = (p1.longitude - p2.longitude) * d2r
    
    a = pow(math.sin(diffLat / 2.0), 2) + math.cos(p1.latitude * d2r) * math.cos(p2.latitude * d2r) * pow(math.sin(diffLong / 2.0), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return 1000.0 * (6371 * c)

def dbm2Double(dbm):
    return math.pow(10, (dbm / 10))

def double2dbm(val):
    return 10 * math.log10(val)

class HataSRDModel:
    def __init__(self):
        self.constant = 69.55
        self.baseStationHeight = 30.0
        self.mobileStationHeight = 1.5
        
    def getDistance(self, antenna, frequency, potency, signalLevel):
        bhb = (1.1 * math.log10(frequency) - 0.7) * min(10.0, self.baseStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.baseStationHeight / 10.0))
        ahm = (1.1 * math.log10(frequency) - 0.7) * min(10.0, self.mobileStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.mobileStationHeight / 10.0))
        hata = potency - signalLevel + antenna
        
        return 1000.0 * pow(10.0, (hata - self.constant - 26.16 * math.log10(frequency) + 13.82 * math.log10(self.baseStationHeight) + ahm + bhb) / (44.9 - 6.55 * math.log10(self.baseStationHeight)))
    
    def getSignalLevel(self, antenna, frequency, potency, distance):
        if (distance < 5.0):
            distance = 5.0
        
        bhb = (1.1 * math.log10(frequency) - 0.7) * min(10.0, self.baseStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.baseStationHeight / 10.0))
        ahm = (1.1 * math.log10(frequency) - 0.7) * min(10.0, self.mobileStationHeight) - (1.56 * math.log10(frequency) - 0.8) + max(0.0, 20.0 * math.log10(self.mobileStationHeight / 10.0))
        hata = self.constant + 26.16 * math.log10(frequency) - 13.82 * math.log10(max(30, self.baseStationHeight)) - ahm + (44.9 - 6.55 * math.log10(max(30, self.baseStationHeight))) * math.log10(distance / 1000) - bhb
        
        return int(((antenna + potency) - hata))
        