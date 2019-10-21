# -*- coding: utf-8 -*-
import argparse

import DataStructures
import Scenario
import PreProcessing
import gurobipy as gb

#import MathUtil
#from sklearn.preprocessing import MinMaxScaler
#import matplotlib.pyplot as plt
#import MiscUtil

#------------------------------ BEGIN ARGUMENTS ------------------------------#

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--cm", type=str, default="input_data/cenarios800/1.1/800_3_10_1_.xml", required=False)
arg_parser.add_argument("--cdis", type=str, default="input_data/CDIS800/CDIS.25.1.1.xml", required=False)

args = arg_parser.parse_args()

#------------------------------ END ARGUMENTS ------------------------------#

#------------------------------ BEGIN LOADING ------------------------------#

print(">>: Carregando cenário")
scenario = Scenario.Scenario()
scenario.read(args.cm, args.cdis)

#------------------------------ END LOADING ------------------------------#

#------------------------------ BEGIN PREPROCESSING ------------------------------#

print(">>: Pré-processando entrada")
(allCEVarList, ceVarList, allCountVarList, interferenceList, testInterferenceList) = PreProcessing.process(scenario)

#------------------------------ END PREPROCESSING ------------------------------#

#------------------------------ BEGIN SOLVER ------------------------------#

print(">>: Criando modelo")
model = gb.Model('cognitive-networks')

print(">>: Adicionando variáveis ao modelo")
modelAllCEVarList = []

for ceVar in allCEVarList:
    modelAllCEVarList.append(model.addVar(name=ceVar.name, vtype=gb.GRB.BINARY))

modelCountVarList = []

for countVar in allCountVarList:
    modelCountVarList.append(model.addVar(name=countVar.name, vtype=gb.GRB.INTEGER))

model.update()

modelCEVarList = []

for ceVars in ceVarList:
    modelVarList = []
    
    for ceVar in ceVars:
        modelVarList.append(model.getVarByName(ceVar.name))
        
    modelCEVarList.append(modelVarList)

print(">>: Adicionando restrições ao modelo")
ceId = 0

for modelCEVars in modelCEVarList:
    model.addConstr(gb.quicksum(modelCEVars), 
                    gb.GRB.EQUAL, 
                    1, 
                    "Configuração_única_para_CE_" + str(ceId))
    
    ceId += 1
    
for modelCountVar in modelCountVarList:
    countVarNameSplit = modelCountVar.varName.split('_')
    
    channel = int(countVarNameSplit[1])
    potency = int(countVarNameSplit[2])
    
    filtredModelCEVarList = PreProcessing.filterModelCEVarByChannelAndPotency(modelAllCEVarList, channel, potency)
        
    model.addConstr(gb.quicksum(filtredModelCEVarList), 
                    gb.GRB.EQUAL, 
                    modelCountVar, 
                    "Variável_" + modelCountVar.varName)
    
    model.addConstr(modelCountVar, 
                    gb.GRB.LESS_EQUAL, 
                    1, 
                    "Valor_da_variável_" + modelCountVar.varName)
        
print(">>: Definindo a função objetivo")
model.setObjective(gb.quicksum(modelCountVarList), gb.GRB.MINIMIZE)

model.write("model.lp")
print(">>: Modelo salvo")

print(">>: Otimizando modelo")
model.optimize()

resultCEVarList = []

if (model.status == gb.GRB.Status.OPTIMAL):
    print(">>: Resultado ótimo:")
    
    for modelCEVar in modelAllCEVarList:
        if(modelCEVar.x == 1):
            resultCEVarList.append(modelCEVar.varName)
            print('%s' % modelCEVar.varName)
            
    for modelCountVar in modelCountVarList:
        print('%s %s' % (modelCountVar.varName, modelCountVar.x))
elif (model.status == gb.GRB.Status.INFEASIBLE):
    print(">>: O modelo é inviável!")
    
    print(">>: Computando IIS")
    model.computeIIS()
      
    print(">>>: As restrições a seguir não foram satisfeitas:")
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)
    
    print(">>>: Otimizando modelo relaxado")        
    model.feasRelaxS(0, False, False, True)
    model.optimize()
    
    if (model.status == gb.GRB.Status.OPTIMAL):
        print(">>>: Resultado ótimo do modelo relaxado:")
    
        for modelCEVar in modelAllCEVarList:
            if(modelCEVar.x == 1):
                resultCEVarList.append(modelCEVar.varName)
                print('%s' % modelCEVar.varName)
        
        for modelCountVar in modelCountVarList:
            print('%s %s' % (modelCountVar.varName, modelCountVar.x))
    elif (model.status in (gb.GRB.Status.INF_OR_UNBD, gb.GRB.Status.UNBOUNDED, gb.GRB.Status.INFEASIBLE)):
        print(">>>: O modelo relaxado não pode ser resolvido porque é ilimitado ou inviável")
        exit(1)
    else:
        print(">>>: A otimização parou com status: %d" % model.status)
        exit(1)
elif (model.status == gb.GRB.Status.UNBOUNDED):
    print(">>>: O modelo não pode ser resolvido porque é ilimitado")
    exit(1)
else:
    print(">>>: A otimização parou com status: %d" % model.status)
    exit(1)

#------------------------------ END SOLVER ------------------------------#
    
#------------------------------ BEGIN VISUALIZATION ------------------------------#

resultCEList = []

for resultCEVar in resultCEVarList:
    ceVarNameSplit = resultCEVar.split('_')
        
    ceId = int(ceVarNameSplit[1])
    resultCEChannelNumber = int(ceVarNameSplit[2])
    resultCEPotency = int(ceVarNameSplit[3])
    
    ce = scenario.cm.ceList[ceId]
    
    resultCEList.append(DataStructures.CE(ceId, ce.antenna, resultCEChannelNumber, ce.geoPoint, resultCEPotency, ce.maxPotency, ce.clientList))

#hataSRD = MathUtil.HataSRDModel() 
#cePointsList = []
#ceChannelList = []
#cePotencyList = []
#ceSignalDistanceList = []
#
#for resultCEVar in resultVarList:
#    ceVarNameSplit = resultCEVar.split('_')
#
#    ceId = int(ceVarNameSplit[1])
#    ceChannel = int(ceVarNameSplit[2])
#    cePotency = int(ceVarNameSplit[3])
#    
#    ce = scenario.cm.ceList[ceId]
#    channelFrequency = next(c.frequency for c in scenario.channels if (c.channelNumber == ceChannel))
#
#    cePointsList.append(MathUtil.latlon_to_xyz(ce.geoPoint.latitude, ce.geoPoint.longitude))
#    ceChannelList.append(ceChannel)
#    cePotencyList.append(cePotency)
#    
#    signalDistance = hataSRD.getDistance(ce.antenna, channelFrequency, cePotency, -50)
#    ceSignalDistanceList.append([signalDistance])
#
#scaler = MinMaxScaler()
#cePointsList = scaler.fit_transform(cePointsList)
#ceSignalDistanceList = scaler.fit_transform(ceSignalDistanceList)
#
#cmap = ["aqua", "blue", "brown", "fuchsia", "gold", "green", "gray", "orange", "salmon", "tomato", "violet"]
#
#circleList = []
#
#for i in range(0, len(cePointsList)):
#    circle = plt.Circle((cePointsList[i][0], cePointsList[i][1]), 0.5 * ceSignalDistanceList[i], color=cmap[ceChannelList[i]], alpha=0.5)
#    circleList.append(circle)
#
#fig, ax = plt.subplots()
#
#for circle in circleList:
#    ax.add_artist(circle)
    
#------------------------------ END VISUALIZATION ------------------------------#