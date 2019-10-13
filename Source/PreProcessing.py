# -*- coding: utf-8 -*-
import MiscUtil
import MathUtil
import DataStructures

def createAllVars(scenario):
    ceVarList = []
    
    ceLength = len(scenario.cm.ceList)
    ceIdList = range(0, ceLength)
    channelList = MiscUtil.range_i(1, 13)
    
    for ceId in ceIdList:
        strCEId = str(ceId)
        
        for channel in channelList:
            strChannel = str(channel)
            
            potencyList = MiscUtil.range_i(1, scenario.cm.ceList[ceId].maxPotency, 1)
            
            for potency in potencyList:
                strPotency = str(potency)
                
                varName = "Y_" + strCEId + "_" + strChannel + "_" + strPotency
                varDescription = "CE com id=" + strCEId + " usando canal=" + strChannel + " com potência=" + strPotency
        
                ceVar = DataStructures.LPVar(varName, varDescription)
                ceVarList.append(ceVar)
        
    return ceVarList

def removeVarsWithUnavailableChannel(scenario, varList):
    newVarList = []
    
    for var in varList:
        varNameSplit = var.name.split('_')
        ceChannel = int(varNameSplit[2])
        
        channel = next(c for c in scenario.channels if (c.channelNumber == ceChannel))
        
        if ((channel.state == DataStructures.ChannelState.AVAILABLE) 
            or (channel.state == DataStructures.ChannelState.OPERATING) 
            or (channel.state == DataStructures.ChannelState.COEXISTENT)):
            newVarList.append(var)

    return newVarList

def removeVarWithLowPotency(scenario, varList):
    hataSRD = MathUtil.HataSRDModel()
    
    maxDistanceCEAndClients = []
    
    for ce in scenario.cm.ceList:
        ceClientDistanceList = []
        
        for ceClient in ce.clientList:
            distanceBetween = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, ceClient.geoPoint)
            ceClientDistanceList.append(distanceBetween)
            
        maxDistance = max(ceClientDistanceList)
        maxDistanceCEAndClients.append(maxDistance)

    newVarList = []
    
    for var in varList:
        varNameSplit = var.name.split('_')
        
        ceId = int(varNameSplit[1])
        cePotency = float(varNameSplit[3])
        
        ce = scenario.cm.ceList[ceId]
        channel = next(c for c in scenario.channels if (c.channelNumber == ce.channel))
        
        ceSignalDistance = hataSRD.getDistance(ce.antenna, channel.frequency, cePotency, -68)
        
        if(ceSignalDistance >= maxDistanceCEAndClients[ceId]):
            newVarList.append(var)
        
    return newVarList
        
def process(scenario):
    ceVarList = createAllVars(scenario)
    ceVarList = removeVarsWithUnavailableChannel(scenario, ceVarList)
    ceVarList = removeVarWithLowPotency(scenario, ceVarList)
    
    return ceVarList