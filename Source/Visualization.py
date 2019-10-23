# -*- coding: utf-8 -*-
import os
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler

import MathUtil

def createRadiusList(maxRadius, division=20):
    radiusList = []
    
    step = maxRadius / division
    totalCount = maxRadius / step
    
    count = 0
    radius = step
    
    while(count < totalCount):
        radiusList.append(radius)
        radius += step
        count += 1
    
    return radiusList

def visualize(scenario, resultCEList, result_fig_path, vis_id):
    hataSRD = MathUtil.HataSRDModel()
        
    cePointsList = []
    ceChannelList = []
    cePotencyList = []
    ceSignalDistanceList = []
    
    for resultCE in resultCEList:
        channelFrequency = next(c.frequency for c in scenario.channels if (c.channelNumber == resultCE.channel))
    
        cePointsList.append(MathUtil.latlon_to_xyz(resultCE.geoPoint.latitude, resultCE.geoPoint.longitude))
        ceChannelList.append(resultCE.channel)
        cePotencyList.append(resultCE.potency)
        ceSignalDistanceList.append([hataSRD.getDistance(resultCE.antenna, channelFrequency, resultCE.potency, -60)])
        
    point_scaler = MinMaxScaler(feature_range=(0, 1))
    cePointsList = point_scaler.fit_transform(cePointsList)
    
    distance_scaler = MinMaxScaler(feature_range=(0, 1))
    ceSignalDistanceList = distance_scaler.fit_transform(ceSignalDistanceList)

    cmap = plt.get_cmap('jet', 13)
    radius = createRadiusList(0.2)
    
    circleList = []
    circleLegendList = []
    
    for i in range(0, len(cePointsList)):
        circle = plt.Circle((cePointsList[i][0], cePointsList[i][1]), radius[cePotencyList[i] - 1], color=cmap(ceChannelList[i] - 1), alpha=0.75)
        
        circleList.append(circle)
        circleLegendList.append("CE_" + str(i) + "_" + str(resultCEList[i].channel) + "_" + str(resultCEList[i].potency))
    
    fig, ax = plt.subplots()
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    for i in range(0, len(circleList)):
        ax.add_patch(circleList[i])

    ax.legend(circleList, circleLegendList, loc='center left', bbox_to_anchor=(1, 0.5), fontsize = 'xx-small')

    plt.xlim((-0.1, 1.1))
    plt.ylim((-0.1, 1.1))
    plt.savefig(os.path.join(result_fig_path, "result_" + vis_id + ".png"), dpi=500)
    plt.close()