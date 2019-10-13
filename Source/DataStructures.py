# -*- coding: utf-8 -*-
from enum import Enum

class ChannelState(Enum):
    UNCLASSIFIED = 0
    AVAILABLE = 1
    PROTECTED = 2
    RESTRICTED = 3
    OPERATING = 4
    COEXISTENT = 5

class Channel:
    def __init__(self, name, number, frequency, state):
        self.name = name
        self.channelNumber = number
        self.frequency = frequency
        self.state = state

class CEClient:
    def __init__(self, id, latitude, longitude, signal, interference):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.signalLevel = signal
        self.co_channel_interference = interference
    
class CE:
    def __init__(self, id, antenna, channel, latitude, longitude, potency, maxPotency, clientList):
        self.id = id
        self.antenna = antenna
        self.channel = channel
        self.latitude = latitude
        self.longitude = longitude
        self.potency = potency
        self.maxPotency = maxPotency
        self.clientList = clientList
    
class CM:
    def __init__(self, id, ceList):
        self.id = id
        self.ceList = ceList

class CDIS:
    def __init__(self, channelList):
        self.channelList = channelList
        
class LPVar:
    def __init__(self, name, description):
        self.name = name
        self.description = description