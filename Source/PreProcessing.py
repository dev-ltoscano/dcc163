# -*- coding: utf-8 -*-
import math

import MiscUtil
import MathUtil
import DataStructures

def createAllCEVars(scenario):
    allCEVarList = []
    
    ceLength = len(scenario.cm.ceList)
    ceIdList = MiscUtil.range_exclusive(0, ceLength)
    channelList = MiscUtil.range_inclusive(1, 13)
    
    for ceId in ceIdList:
        strCEId = str(ceId)
        
        for channel in channelList:
            strChannel = str(channel)
            
            potencyList = MiscUtil.range_inclusive(1, int(scenario.cm.ceList[ceId].maxPotency), 1)
            
            for potency in potencyList:
                strPotency = str(potency)
                
                varName = "CE_" + strCEId + "_" + strChannel + "_" + strPotency
                varDescription = "CE com id=" + strCEId + " usando canal=" + strChannel + " com potência=" + strPotency
        
                ceVar = DataStructures.LPVar(varName, varDescription)
                allCEVarList.append(ceVar)
        
    return allCEVarList

def removeVarsWithUnavailableChannel(scenario, allCEVarList):
    newCEVarList = []
    
    availableChannelNumberList = [c.channelNumber for c in scenario.channels if ((c.state == DataStructures.ChannelState.AVAILABLE) 
                                                                                or (c.state == DataStructures.ChannelState.OPERATING) 
                                                                                or (c.state == DataStructures.ChannelState.COEXISTENT))]
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        ceChannelNumber = int(ceVarNameSplit[2])
        
        if (ceChannelNumber in availableChannelNumberList):
            newCEVarList.append(ceVar)

    return newCEVarList

def removeVarWithLowPotency(scenario, allCEVarList):
    hataSRD = MathUtil.HataSRDModel()
    
    maxDistanceCEAndClients = []
    
    for ce in scenario.cm.ceList:
        ceClientDistanceList = []
        
        for ceClient in ce.clientList:
            distanceBetween = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, ceClient.geoPoint)
            ceClientDistanceList.append(distanceBetween)
            
        maxDistance = max(ceClientDistanceList)
        maxDistanceCEAndClients.append(maxDistance)

    newCEVarList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        cePotency = float(ceVarNameSplit[3])
        
        ceAntenna = scenario.cm.ceList[ceId].antenna
        channelFrequency = next(c.frequency for c in scenario.channels if (c.channelNumber == ce.channel))
        
        ceSignalDistance = hataSRD.getDistance(ceAntenna, channelFrequency, cePotency, -50)
        
        if(ceSignalDistance >= maxDistanceCEAndClients[ceId]):
            newCEVarList.append(ceVar)
        else:
            print("Removida: " + ceVar.name)
        
    return newCEVarList

def getCEVarList(scenario, allCEVarList):
    ceVarList = []
    
    ceIdList = MiscUtil.range_exclusive(0, len(scenario.cm.ceList))
    
    for ceId in ceIdList:
        varList = [ceVar for ceVar in allCEVarList if ceVar.name.startswith("CE_" + str(ceId) + "_")]
        ceVarList.append(varList)
    
    return ceVarList

def getInterferenceList(scenario, allCEVarList):
    hataSRD = MathUtil.HataSRDModel()
    interferenceList = []
#    testInterferenceList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        ceChannel = int(ceVarNameSplit[2])
        cePotency = int(ceVarNameSplit[3])
        
        ce = scenario.cm.ceList[ceId]
        channel = next(c for c in scenario.channels if c.channelNumber == ceChannel)
        
        sameChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                    and int(c.name.split('_')[2]) == ceChannel]
        
        coChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                    and (int(c.name.split('_')[2]) == (ceChannel - 1) 
                                                        or int(c.name.split('_')[2]) == (ceChannel + 1))]
        
        coCoChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                    and (int(c.name.split('_')[2]) == (ceChannel - 2) 
                                                        or int(c.name.split('_')[2]) == (ceChannel + 2))]
        
        totalInterference = 0
        
        for otherCEVar in sameChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, otherCE.geoPoint)
            signalLevelOtherCE = hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs)
            
            interference = math.pow(10.0, (signalLevelOtherCE / 10.0))
            totalInterference += interference
        
        for otherCEVar in coChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, otherCE.geoPoint)
            signalLevelOtherCE = hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs)
            
            interference = 0.7 * math.pow(10.0, (signalLevelOtherCE / 10.0))
            totalInterference += interference
        
        for otherCEVar in coCoChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, otherCE.geoPoint)
            signalLevelOtherCE = hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs)
            
            interference = 0.3 * math.pow(10.0, (signalLevelOtherCE / 10.0))
            totalInterference += interference
        
        
#        if (totalInterference != 0):
#            totalInterference = 10 * math.log10(totalInterference)
        
        interferenceList.append(totalInterference)
        
    return interferenceList
        
    
def process(scenario):
    allCEVarList = createAllCEVars(scenario)
    allCEVarList = removeVarsWithUnavailableChannel(scenario, allCEVarList)
    allCEVarList = removeVarWithLowPotency(scenario, allCEVarList)
    
    ceVarList = getCEVarList(scenario, allCEVarList)
    
    interferenceList = getInterferenceList(scenario, allCEVarList)
    
    return (allCEVarList, ceVarList, interferenceList)