# -*- coding: utf-8 -*-
import MiscUtil
import MathUtil
import DataStructures

def createAllCEVars(scenario):
    ceVarList = []
    
    ceLength = len(scenario.cm.ceList)
    ceIdList = range(0, ceLength)
    channelList = MiscUtil.range_i(1, 13)
    
    for ceId in ceIdList:
        strCEId = str(ceId)
        
        for channel in channelList:
            strChannel = str(channel)
            
            potencyList = MiscUtil.range_i(1, int(scenario.cm.ceList[ceId].maxPotency), 1)
            
            for potency in potencyList:
                strPotency = str(potency)
                
                varName = "CE_" + strCEId + "_" + strChannel + "_" + strPotency
                varDescription = "CE com id=" + strCEId + " usando canal=" + strChannel + " com potência=" + strPotency
        
                ceVar = DataStructures.LPVar(varName, varDescription)
                ceVarList.append(ceVar)
        
    return ceVarList

def removeVarsWithUnavailableChannel(scenario, allCEVarList):
    newCEVarList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        ceChannel = int(ceVarNameSplit[2])
        
        channel = next(c for c in scenario.channels if (c.channelNumber == ceChannel))
        
        if ((channel.state == DataStructures.ChannelState.AVAILABLE) 
            or (channel.state == DataStructures.ChannelState.OPERATING) 
            or (channel.state == DataStructures.ChannelState.COEXISTENT)):
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
        
        ce = scenario.cm.ceList[ceId]
        channel = next(c for c in scenario.channels if (c.channelNumber == ce.channel))
        
        ceSignalDistance = hataSRD.getDistance(ce.antenna, channel.frequency, cePotency, -68)
        
        if(ceSignalDistance >= maxDistanceCEAndClients[ceId]):
            newCEVarList.append(ceVar)
        
    return newCEVarList

def getCEVarList(scenario, allCEVarList):
    ceVarList = []
    
    for i in range(0, len(scenario.cm.ceList)):
        varList = [v for v in allCEVarList if v.name.startswith("CE_" + str(i))]
        ceVarList.append(varList)
    
    return ceVarList

def countCEConfigs(scenario, allCEVarList):
    countConfigList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceChannel = int(ceVarNameSplit[2])
        cePotency = float(ceVarNameSplit[3])
        
        config_id = ceVarNameSplit[2] + "_" + ceVarNameSplit[3]
        config_count = len([ce for ce in scenario.cm.ceList if ((ce.channel == ceChannel) and (ce.potency == cePotency))])
        
        countConfigList.append((config_id, config_count))
        
    return countConfigList
    
def getInterferenceList(scenario, allCEVarList):
    hataSRD = MathUtil.HataSRDModel()
    interferenceList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        ceChannel = int(ceVarNameSplit[2])
        cePotency = float(ceVarNameSplit[3])
        
        for otherCEVar in allCEVarList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEChannel = int(otherCEVarNameSplit[2])
            otherCEPotency = float(otherCEVarNameSplit[3])
            
            if((otherCEId > ceId) and (otherCEChannel == ceChannel)):
                channel = next(c for c in scenario.channels if (c.channelNumber == ceChannel))
                
                ce = scenario.cm.ceList[ceId]
                ceSignalDistance = hataSRD.getDistance(ce.antenna, channel.frequency, cePotency, -68)
                
                otherCE = scenario.cm.ceList[otherCEId]
                otherCESignalDistance = hataSRD.getDistance(otherCE.antenna, channel.frequency, otherCEPotency, -68)
                
                distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, otherCE.geoPoint)
                
                if(ceSignalDistance + otherCESignalDistance >= distanceBetweenCEs):
                    interferenceList.append((ceVar, otherCEVar))
                
    return interferenceList
  
def process(scenario):
    allCEVarList = createAllCEVars(scenario)
    allCEVarList = removeVarsWithUnavailableChannel(scenario, allCEVarList)
    allCEVarList = removeVarWithLowPotency(scenario, allCEVarList)
    
    ceVarList = getCEVarList(scenario, allCEVarList)
    countCEConfigs(scenario, allCEVarList)
    
    interferenceCEVarList = getInterferenceList(scenario, allCEVarList)
    
    return (allCEVarList, ceVarList, interferenceCEVarList)