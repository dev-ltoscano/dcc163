# -*- coding: utf-8 -*-
import argparse

import Scenario
import PreProcessing
import gurobipy as gb

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
(allCEVarList, ceVarList, interferenceList) = PreProcessing.process(scenario)

#------------------------------ END PREPROCESSING ------------------------------#

#------------------------------ BEGIN SOLVER ------------------------------#

print(">>: Criando modelo...")
model = gb.Model('cognitive-networks')

print(">>: Adicionando variáveis ao modelo")
for ceVar in allCEVarList:
    model.addVar(name=ceVar.name, vtype=gb.GRB.BINARY)

model.update()

print(">>: Adicionando restrições ao modelo")
ceId = 0

for ceVars in ceVarList:
    modelCEVarList = []
    
    for ceVar in ceVars:
        modelCEVarList.append(model.getVarByName(ceVar.name))
    
    model.addConstr(gb.quicksum(modelCEVarList), 
                    gb.GRB.EQUAL, 
                    1, 
                    "Configuração_única_para_CE_" + str(ceId))
    ceId += 1
        
print(">>: Definindo a função objetivo")
modelCEVarList = []
    
for ceVar in allCEVarList:
    modelCEVarList.append(model.getVarByName(ceVar.name))

objList = []

for i in range(0, len(allCEVarList)):
    objList.append(interferenceList[i] * modelCEVarList[i])
    
model.setObjective(gb.quicksum(objList), gb.GRB.MINIMIZE)

model.write("model.lp")
print(">>: Modelo salvo")

print(">>: Otimizando...")
model.optimize()

status = model.status

if status == gb.GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
elif status == gb.GRB.Status.OPTIMAL:
    print('The optimal objective is %g' % model.objVal)
    
    print(">>: Resultado:")
    
    for varModel in model.getVars():
        if(varModel.x == 1):
            print('%s %g' % (varModel.varName, varModel.x))
elif status != gb.GRB.Status.INF_OR_UNBD and status != gb.GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
else:
    print('The model is infeasible; computing IIS')
    model.computeIIS()
    if model.IISMinimal:
      print('IIS is minimal\n')
    else:
      print('IIS is not minimal\n')
    print('\nThe following constraint(s) cannot be satisfied:')
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)

#------------------------------ END SOLVER ------------------------------#