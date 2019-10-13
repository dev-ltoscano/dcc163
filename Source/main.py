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
(allCEVarList, ceVarList, interferenceCEVarList) = PreProcessing.process(scenario)

#------------------------------ END PREPROCESSING ------------------------------#

#------------------------------ BEGIN SOLVER ------------------------------#

print(">>: Criando modelo...")
model = gb.Model('cognitive-networks')

print(">>: Adicionando variáveis ao modelo")
for ceVar in allCEVarList:
    model.addVar(name=ceVar.name, vtype=gb.GRB.BINARY)

model.update()

print(">>: Adicionando restrições ao modelo")
index = 0

for ceVars in ceVarList:
    modelCEVarList = []
    
    for ceVar in ceVars:
        modelCEVar = model.getVarByName(ceVar.name)
        modelCEVarList.append(modelCEVar)
    
    model.addConstr(gb.quicksum(modelCEVarList), 
                    gb.GRB.EQUAL, 
                    1, 
                    "Único_canal_e_potência_para_CE_" + str(index))
    index += 1

for interference in interferenceCEVarList:
    model.addConstr(model.getVarByName(interference[0].name) + model.getVarByName(interference[1].name), 
                    gb.GRB.LESS_EQUAL, 1, 
                    "Interferência_entre_" + interference[0].name + "_e_" + interference[1].name)

#print(">>: Otimizando...")
#model.optimize()
#
#print(">>: Resultado:")
#for varModel in model.getVars():
#    print('%s %g' % (varModel.varName, varModel.x))

model.write("model.lp")
print(">>: Modelo salvo")

#------------------------------ END SOLVER ------------------------------#