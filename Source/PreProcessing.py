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

def createAllCEByChannelVars(scenario, allCEVarList):
    ceByChannelVarList = []
    ceByChannelVarNameList = []

    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        ceVarName = "CEs_NO_CANAL_" + ceVarNameSplit[2]
        
        if(ceVarName not in ceByChannelVarNameList):
            ceByChannelVarNameList.append(ceVarName)
            
    for ceVarName in ceByChannelVarNameList:
        ceByChannelVarList.append(DataStructures.LPVar(ceVarName, "Quantide de CEs no canal=" + ceVarName.split('_')[3]))
        
    return ceByChannelVarList

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
        cePotency = int(ceVarNameSplit[3])
        
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

def filterCEByChannelModelVar(modelCEVarList, channel):
    filtredCEVarList = []
    
    for modelCEVar in modelCEVarList:
        ceVarNameSplit = modelCEVar.varName.split('_')
        
        ceChannel = int(ceVarNameSplit[2])
        
        if (ceChannel == channel):
            filtredCEVarList.append(modelCEVar)
            
    return filtredCEVarList

def countAvailableChannels(scenario):
    return len([c.channelNumber for c in scenario.channels if ((c.state == DataStructures.ChannelState.AVAILABLE) 
                                                                                or (c.state == DataStructures.ChannelState.OPERATING) 
                                                                                or (c.state == DataStructures.ChannelState.COEXISTENT))])

def getInterferenceList(scenario, allCEVarList):
    hataSRD = MathUtil.HataSRDModel()
    interferenceList = []
    
    for ceVar in allCEVarList:
        ceVarNameSplit = ceVar.name.split('_')
        
        ceId = int(ceVarNameSplit[1])
        ceChannel = int(ceVarNameSplit[2])
        cePotency = int(ceVarNameSplit[3])
        
        ce = scenario.cm.ceList[ceId]
        channel = next(c for c in scenario.channels if c.channelNumber == ceChannel)
        ceSignalDistance = hataSRD.getDistance(ce.antenna, channel.frequency, cePotency, -60)
        
        ceTotalInterference = 0.0
        ceInterferenceList = []
        
        for otherCEVar in allCEVarList:
            otherCEVarNameSplit = otherCEVar.name.split('_')
        
            otherCEId = int(otherCEVarNameSplit[1])
            otherCEChannel = int(otherCEVarNameSplit[2])
            
            if(otherCEId != ceId):
                otherCE = scenario.cm.ceList[otherCEId]
                distanceBetweenCEs = MathUtil.calculateDistanceBetweenGeoPoints(ce.geoPoint, otherCE.geoPoint)
                signalLevel = MathUtil.dbm2Double(hataSRD.getSignalLevel(ce.antenna, channel.frequency, cePotency, distanceBetweenCEs))
                
                if(ceSignalDistance >= distanceBetweenCEs):
                    if(otherCEChannel == ceChannel):
                        signalLevel = 1.0 * signalLevel
                        ceTotalInterference += signalLevel
                        ceInterferenceList.append(signalLevel)
                    elif (otherCEChannel == (ceChannel - 1)) or (otherCEChannel == (ceChannel + 1)):
                        signalLevel = 0.7 * signalLevel
                        ceTotalInterference += signalLevel
                        ceInterferenceList.append(signalLevel)
                    elif (otherCEChannel == (ceChannel - 2)) or (otherCEChannel == (ceChannel + 2)):
                        signalLevel = 0.3 * signalLevel
                        ceTotalInterference += signalLevel
                        ceInterferenceList.append(signalLevel)
                        
        interferenceList.append((ceVar, ceTotalInterference, ceInterferenceList))
                        
    return interferenceList
   
def process(scenario):
    allCEVarList = createAllCEVars(scenario)
    allCEVarList = removeVarsWithUnavailableChannel(scenario, allCEVarList)
    allCEVarList = removeVarWithLowPotency(scenario, allCEVarList)
    ceVarList = filterCEVarList(scenario, allCEVarList)
    
    qtdCEByChannelVarList = createAllCEByChannelVars(scenario, allCEVarList)
    
    interferenceList = getInterferenceList(scenario, allCEVarList)
    
    return (allCEVarList, ceVarList, qtdCEByChannelVarList, interferenceList)