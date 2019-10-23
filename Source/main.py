# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import time

from datetime import datetime

import DataStructures
import Scenario
import PreProcessing
import gurobipy as gb
import Visualization

#------------------------------ BEGIN ARGUMENTS ------------------------------#

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--cm", type=str, default="input_data/cenarios800/1.1/800_3_10_1_.xml", required=False)
arg_parser.add_argument("--cdis", type=str, default="input_data/CDIS800/CDIS.25.1.1.xml", required=False)
arg_parser.add_argument("--out_dir", type=str, default="output_data/", required=False)
arg_parser.add_argument("--max_interference", type=float, default=1e-5, required=False)
arg_parser.add_argument("--min_potency", type=int, default=1, required=False)

args = arg_parser.parse_args()

#------------------------------ END ARGUMENTS ------------------------------#

def main(cm_file, cdis_file, output_dir):
    #------------------------------ BEGIN LOADING ------------------------------#
    
    print(">>>: Carregando cenário")
    scenario = Scenario.Scenario()
    scenario.read(cm_file, cdis_file)
    
    scenario_name = os.path.splitext(os.path.basename(cm_file))[0]
    cdis_info_name = os.path.splitext(os.path.basename(cdis_file))[0]
    
    scenario_path = os.path.join(output_dir, scenario_name + cdis_info_name)
    
    result_log_path = os.path.join(scenario_path, "result_log.csv")
    result_fig_path = os.path.join(scenario_path, "figures")
    result_res_path = os.path.join(scenario_path, "results")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(scenario_path):
        os.makedirs(scenario_path)
    else:
        shutil.rmtree(scenario_path)
        os.makedirs(scenario_path)
        
    if not os.path.exists(result_fig_path):
        os.makedirs(result_fig_path)
        
    if not os.path.exists(result_res_path):
        os.makedirs(result_res_path)
        
    Visualization.visualize(scenario, scenario.cm.ceList, result_fig_path, "00")
    
    #------------------------------ END LOADING ------------------------------#
        
    with open(result_log_path, "w+") as resultLogFile:
        resultLogFile.write("Data_e_Hora;Nome_do_cenário;Caminho_do_arquivo_do_cenário;Nome_das_informações_do_CDIS;Caminho_do_arquivo_das_informações_do_cdis;Tempo_de_execução\n")
        resultLogFile.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ";" + scenario_name + ";" + cm_file + ";" + cdis_info_name + ";" + cdis_file)
        
        startTime = time.time()
        totalIteration = len(scenario.cdisList)
        
        for iteration in range(0, totalIteration):
            print("\n>>>: Resolvendo cenário com informações do CDIS=" + str(iteration) + "/" + str(totalIteration))
            scenario.updateChannels(scenario.cdisList[iteration].channelList)
            
            #------------------------------ BEGIN PREPROCESSING ------------------------------#
            
            print(">>>: Pré-processando entrada")
            (allCEVarList, ceVarList, ceByChannelVarList, interferenceList) = PreProcessing.process(scenario)
            
            #------------------------------ END PREPROCESSING ------------------------------#
            
            #------------------------------ BEGIN SOLVER ------------------------------#
            
            print(">>>: Criando modelo")
            model = gb.Model('cognitive-networks')
            
            print(">>>: Adicionando variáveis ao modelo")
            allCEModelVarList = []
            
            for ceVar in allCEVarList:
                allCEModelVarList.append(model.addVar(name=ceVar.name, vtype=gb.GRB.BINARY))
                
            ceByChannelModelVarList = []
            
            for ceByChannelVar in ceByChannelVarList:
                ceByChannelModelVarList.append(model.addVar(name=ceByChannelVar.name))
            
            model.update()
            
            ceModelVarList = []
            
            for ceVars in ceVarList:
                modelVarList = []
                
                for ceVar in ceVars:
                    modelVarList.append(model.getVarByName(ceVar.name))
                    
                ceModelVarList.append(modelVarList)
            
            print(">>>: Adicionando restrições ao modelo")
            ceId = 0
            
            for ceModelVars in ceModelVarList:
                model.addConstr(gb.quicksum(ceModelVars), 
                                gb.GRB.EQUAL, 
                                1, 
                                "Única_configuração_para_CE_" + str(ceId))
                
                ceId += 1
            
            interferenceModelVarList = []
            
            for interference in interferenceList:
                ceVar = interference[0]
                ceTotalInterference = interference[1]
                ceInterferenceList = interference[2]
                
                if (ceTotalInterference > 0):
                    interferenceModelVar = model.addVar(name="Interferência-devido-" + ceVar.name)
                    interferenceModelVarList.append(interferenceModelVar)
                    model.update()
                    
                    ceInterferenceModelVarList = []
                    
                    for ceInterference in ceInterferenceList:
                        ceInterferenceModelVarList.append(ceInterference * model.getVarByName(ceVar.name))
                    
                    model.addConstr(gb.quicksum(ceInterferenceModelVarList), 
                                    gb.GRB.EQUAL, 
                                    interferenceModelVar, 
                                    "Interferência_provocada_por_" + ceVar.name)
                    
                    model.addConstr(interferenceModelVar, 
                                    gb.GRB.LESS_EQUAL, 
                                    args.max_interference, 
                                    "Máximo_de_interferência_tolerada_de_" + ceVar.name)
                    
            for ceByChannelModelVar in ceByChannelModelVarList:
                ceByChannelVarNameSplit = ceByChannelModelVar.varName.split('_')
                
                channel = int(ceByChannelVarNameSplit[3])
                
                filtredCEModelVarList = PreProcessing.filterCEByChannelModelVar(allCEModelVarList, channel)
                    
                model.addConstr(gb.quicksum(filtredCEModelVarList), 
                                gb.GRB.EQUAL, 
                                ceByChannelModelVar, 
                                "Qtd_de_CE_no_canal_" + str(channel))
                
                model.addConstr(ceByChannelModelVar, 
                                gb.GRB.LESS_EQUAL, 
                                min(len(scenario.cm.ceList), ((len(scenario.cm.ceList) / PreProcessing.countAvailableChannels(scenario)) + 1)), 
                                "Máximo_de_CEs_no_canal_" + str(channel))
            
            ceId = 0
            
            for ceModelVars in ceModelVarList:
                potencyList = []
                
                for ceModelVar in ceModelVars:
                    ceModelVarNameSplit = ceModelVar.varName.split("_")
                    cePotency = int(ceModelVarNameSplit[3])
                    potencyList.append(cePotency * ceModelVar)
                
                model.addConstr(gb.quicksum(potencyList), 
                                gb.GRB.GREATER_EQUAL, 
                                args.min_potency, 
                                "Mínimo_de_potência_para_máxima_cobertura_do_CE_" + str(ceId))
                
                ceId += 1
                
            print(">>>: Definindo a função objetivo")
            model.setObjective(gb.quicksum(interferenceModelVarList), gb.GRB.MINIMIZE)
            
            model.write(os.path.join(result_res_path, "model_it_" + str(iteration) + ".lp"))
            print(">>>: Modelo salvo")
            
            print(">>>: Otimizando modelo")
            model.optimize()
            
            resultCEVarList = []
            
            with open(os.path.join(result_res_path, "it_" + str(iteration) + ".txt"), "w") as resultFile:
                if (model.status == gb.GRB.Status.OPTIMAL):
                    resultFile.write(">>>: Resultado ótimo:\n")
                    print(">>>: Resultado ótimo:")
                    
                    for ceModelVar in allCEModelVarList:
                        if(ceModelVar.x == 1.0):
                            resultCEVarList.append(ceModelVar.varName)
                            resultFile.write("%s\n" % ceModelVar.varName)
                            print("%s" % ceModelVar.varName)
                            
                    for interferenceModelVar in interferenceModelVarList:
                        ceModelVar = model.getVarByName(interferenceModelVar.varName.split("-")[2])
                        
                        if((ceModelVar.x == 1.0) and (interferenceModelVar.x > 0.0)):
                            resultFile.write("%s %s\n" % (interferenceModelVar.varName, interferenceModelVar.x))
                            print("%s %s" % (interferenceModelVar.varName, interferenceModelVar.x))
                            
                    for ceByChannelModelVar in ceByChannelModelVarList:
                        resultFile.write("%s %s\n" % (ceByChannelModelVar.varName, ceByChannelModelVar.x))
                        print("%s %s" % (ceByChannelModelVar.varName, ceByChannelModelVar.x))
                elif (model.status == gb.GRB.Status.INFEASIBLE):
                    resultFile.write(">>>: O modelo é inviável!\n")
                    print(">>>: O modelo é inviável!")
                    
                    print(">>>: Computando IIS")
                    model.computeIIS()
                    
                    resultFile.write("\n>>>: As restrições a seguir não foram satisfeitas:\n")
                    print(">>>: As restrições a seguir não foram satisfeitas:")
                    for c in model.getConstrs():
                        if c.IISConstr:
                            resultFile.write("%s\n" % c.constrName)
                            print("%s" % c.constrName)
                    
                    print(">>>: Otimizando modelo relaxado")
                    model.feasRelaxS(0, False, False, True)
                    model.optimize()
                    
                    if (model.status == gb.GRB.Status.OPTIMAL):
                        resultFile.write("\n>>>: Resultado ótimo do modelo relaxado:\n")
                        print(">>>: Resultado ótimo do modelo relaxado:")
                    
                        for ceModelVar in allCEModelVarList:
                            if(ceModelVar.x == 1.0):
                                resultCEVarList.append(ceModelVar.varName)
                                resultFile.write("%s\n" % ceModelVar.varName)
                                print("%s" % ceModelVar.varName)
                            
                        for interferenceModelVar in interferenceModelVarList:
                            ceModelVar = model.getVarByName(interferenceModelVar.varName.split("-")[2])
                            
                            if((ceModelVar.x == 1.0) and (interferenceModelVar.x > 0.0)):
                                resultFile.write("%s %s\n" % (interferenceModelVar.varName, interferenceModelVar.x))
                                print("%s %s" % (interferenceModelVar.varName, interferenceModelVar.x))
                                
                        for ceByChannelModelVar in ceByChannelModelVarList:
                            resultFile.write("%s %s\n" % (ceByChannelModelVar.varName, ceByChannelModelVar.x))
                            print("%s %s" % (ceByChannelModelVar.varName, ceByChannelModelVar.x))
                    elif (model.status in (gb.GRB.Status.INF_OR_UNBD, gb.GRB.Status.UNBOUNDED, gb.GRB.Status.INFEASIBLE)):
                        print(">>>: O modelo relaxado não pode ser resolvido porque é ilimitado ou inviável")
                    else:
                        resultFile.write(">>>: A otimização parou com status: %d\n" % model.status)
                        print(">>>: A otimização parou com status: %d" % model.status)
                elif (model.status == gb.GRB.Status.UNBOUNDED):
                    resultFile.write(">>>: O modelo não pode ser resolvido porque é ilimitado\n")
                    print(">>>: O modelo não pode ser resolvido porque é ilimitado")
                else:
                    resultFile.write(">>>: A otimização parou com status: %d\n" % model.status)
                    print(">>>: A otimização parou com status: %d" % model.status)
            
            resultCEList = []
            
            for resultCEVar in resultCEVarList:
                ceVarNameSplit = resultCEVar.split('_')
                    
                ceId = int(ceVarNameSplit[1])
                resultCEChannelNumber = int(ceVarNameSplit[2])
                resultCEPotency = int(ceVarNameSplit[3])
                
                ce = scenario.cm.ceList[ceId]
                
                resultCEList.append(DataStructures.CE(ceId, ce.antenna, resultCEChannelNumber, ce.geoPoint, resultCEPotency, ce.maxPotency, ce.clientList))
            
            #------------------------------ END SOLVER ------------------------------#
                
            #------------------------------ BEGIN VISUALIZATION ------------------------------#
            
            if(len(resultCEVarList) > 0):
                Visualization.visualize(scenario, resultCEList, result_fig_path, str(iteration))
                
            #------------------------------ END VISUALIZATION ------------------------------#
            
        resultLogFile.write(";" + str((time.time() - startTime)))

main(args.cm, args.cdis, args.out_dir)