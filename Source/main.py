# -*- coding: utf-8 -*-
import Scenario
import PreProcessing

scenario = Scenario.Scenario()
scenario.read("input_data/cenarios800/1.1/800_3_10_1_.xml", "input_data/CDIS800/CDIS.25.1.1.xml")

ceVarList = PreProcessing.process(scenario)