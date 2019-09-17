# -*- coding: utf-8 -*-

"""
@author: ltosc
"""

from enum import Enum
import xml.etree.ElementTree as ET

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
        
class Scenario():
    def __init__(self):
        self.cm = None
        self.channels = None
        
    def read(self, cm_xml_path):
        xmlTree = ET.parse(cm_xml_path)
        xmlRoot = xmlTree.getroot()
        
        ceList = []
        
        for ceElement in xmlRoot.findall('ceList'):
            ceClientList = []
            
            for ceClientElement in ceElement.findall('CEClientList'):
                id = ceClientElement.find('id').text
                latitude = float(ceClientElement.find('latitude').text)
                longitude = float(ceClientElement.find('longitude').text)
                signal = int(ceClientElement.find('nivelSinal').text)
                interference = float(ceClientElement.find('interferenciaCocanal').text)
                
                ceClient = CEClient(id, latitude, longitude, signal, interference)
                
                ceClientList.append(ceClient)
            
            id = ceElement.find('id').text
            antenna = ceElement.find('antena').text
            channel = int(ceElement.find('device').find('canal').text)
            latitude = float(ceElement.find('latitude').text)
            longitude = float(ceElement.find('longitude').text)
            potency = int(ceElement.find('potencia').text)
            maxPotency = int(ceElement.find('potenciaMax').text)
            
            ce = CE(id, antenna, channel, latitude, longitude, potency, maxPotency, ceClientList)
            
            ceList.append(ce)
        
        id = xmlRoot.find('id').text  
        self.cm = CM(id, ceList)
        
        channelList = []
        
        for channelElement in xmlRoot.findall('channels'):
            name = channelElement.find('nome').text
            number = channelElement.find('numCanal').text
            frequency = channelElement.find('frequencia').text
            state = ChannelState[channelElement.find('estado').text]
            
            channel = (name, number, frequency, state)
            
            channelList.append(channel)
        
        self.channels = channelList
        
        
scenario = Scenario()
scenario.read("input_data/cenarios800/1.1/800_3_10_1_.xml")

for channel in scenario.channels:
    print(channel[0])
    print(channel[2])
    print(channel[3])
    print()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        