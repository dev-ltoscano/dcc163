# -*- coding: utf-8 -*-
import MiscUtil
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
        
def preprocess(scenario):
    ceVarList = createAllVars(scenario)
    ceVarList = removeVarsWithUnavailableChannel(scenario, ceVarList)
    
    return ceVarList