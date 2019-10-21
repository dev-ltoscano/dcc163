# -*- coding: utf-8 -*-
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

def createAllCountVars(scenario, allCEVarList):
    countVarList = []

    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        countVarName = "COUNT_" + ceVarNameSplit[2] + "_" + ceVarNameSplit[3]
        countVarDescription = "Contagem de nós por canal=" + ceVarNameSplit[2] + " e potência=" + ceVarNameSplit[3]
        
        countVarList.append(DataStructures.LPVar(countVarName, countVarDescription))
        
    return countVarList

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
        clientDistanceList = []
        
        for ceClient in ce.clientList:
            distanceBetween = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, ceClient.geoPoint)
            clientDistanceList.append(distanceBetween)
            
        maxClientDistance = max(clientDistanceList)
        maxDistanceCEAndClients.append(maxClientDistance)

    newCEVarList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        cePotency = float(ceVarNameSplit[3])
        
        ceAntenna = scenario.cm.ceList[ceId].antenna
        channelFrequency = next(c.frequency for c in scenario.channels if (c.channelNumber == ce.channel))
        
        ceSignalDistance = hataSRD.getDistance(ceAntenna, channelFrequency, cePotency, -60)
        
        if(ceSignalDistance >= maxDistanceCEAndClients[ceId]):
            newCEVarList.append(ceVar)
        
    return newCEVarList

def filterCEVarList(scenario, allCEVarList):
    ceVarList = []
    
    ceIdList = MiscUtil.range_exclusive(0, len(scenario.cm.ceList))
    
    for ceId in ceIdList:
        varList = [ceVar for ceVar in allCEVarList if ceVar.name.startswith("CE_" + str(ceId) + "_")]
        ceVarList.append(varList)
    
    return ceVarList

def filterModelCEVarByChannelAndPotency(modelCEVarList, channel, potency):
    filtredCEVarList = []
    
    for modelCEVar in modelCEVarList:
        ceVarNameSplit = modelCEVar.varName.split('_')
        
        ceChannel = int(ceVarNameSplit[2])
        cePotency = int(ceVarNameSplit[3])
        
        if (ceChannel == channel) and (cePotency == potency):
            filtredCEVarList.append(modelCEVar)
            
    return filtredCEVarList
    
def getInterferenceList(scenario, allCEVarList):
    hataSRD = MathUtil.HataSRDModel()
    interferenceList = []
    testInterferenceList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        ceChannel = int(ceVarNameSplit[2])
        ceGeoPoint = scenario.cm.ceList[ceId].geoPoint
        channel = next(c for c in scenario.channels if c.channelNumber == ceChannel)
        
        sameChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                        and int(c.name.split('_')[2]) == ceChannel]
        
        adjChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                        and (int(c.name.split('_')[2]) == (ceChannel - 1) 
                                                        or int(c.name.split('_')[2]) == (ceChannel + 1))]
        
        adjAdjChannelList = [c for c in allCEVarList if (int(c.name.split('_')[1]) != ceId) 
                                                        and (int(c.name.split('_')[2]) == (ceChannel - 2) 
                                                        or int(c.name.split('_')[2]) == (ceChannel + 2))]

        totalInterference = 0.0
        
        for otherCEVar in sameChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ceGeoPoint, otherCE.geoPoint)
            interference = MathUtil.dbm2Double(hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs))
            
            totalInterference += interference
            
            testInterferenceList.append((otherCEVar.name, interference))
        
        for otherCEVar in adjChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ceGeoPoint, otherCE.geoPoint)
            interference = MathUtil.dbm2Double(hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs))
            
            totalInterference += 0.7 * interference
            
            testInterferenceList.append((otherCEVar.name, interference))
        
        for otherCEVar in adjAdjChannelList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
            
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEPotency = int(otherCEVarNameSplit[3])
            
            otherCE = scenario.cm.ceList[otherCEId]
            distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ceGeoPoint, otherCE.geoPoint)
            interference = MathUtil.dbm2Double(hataSRD.getSignalLevel(otherCE.antenna, channel.frequency, otherCEPotency, distanceBetweenCEs))
            
            totalInterference += 0.3 * interference
            
            testInterferenceList.append((otherCEVar.name, interference))
        
        interferenceList.append(totalInterference)
        
    return interferenceList, testInterferenceList
        
    
def process(scenario):
    allCEVarList = createAllCEVars(scenario)
    allCEVarList = removeVarsWithUnavailableChannel(scenario, allCEVarList)
    allCEVarList = removeVarWithLowPotency(scenario, allCEVarList)
    ceVarList = filterCEVarList(scenario, allCEVarList)
    
    allCountVarList = createAllCountVars(scenario, allCEVarList)
    
    interferenceList, testInterferenceList = getInterferenceList(scenario, allCEVarList)
    
    return (allCEVarList, ceVarList, allCountVarList, interferenceList, testInterferenceList)