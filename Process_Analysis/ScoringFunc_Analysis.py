from PathAndDir import Dir2LineGraph, Path2SelectedSerial, Dir2ViterbiOutFile
import os
import igraph as ig
import numpy as np
from MyIO import ReadViterbiOutFile
import matplotlib.pyplot as plt
import statsmodels.api as sm

if __name__=='__main__':
    ''' Analyse the relationship btw score of Truth Lable and score of Viterbi Label'''
    #L = [int(f.split('.')[0]) for f in os.listdir(Dir2ViterbiOutFile) if
    #                os.path.isfile(os.path.join(Dir2ViterbiOutFile, f))]
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    TruthLabelScores = []
    ViterbiLabelScores = []
    for serial in L:
        Path2LineGraphFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
        LineG = ig.Graph().Read_Picklez(Path2LineGraphFile)
        TrueLabel = LineG.vs['TrueLabel']
        ViterbiLabel = ReadViterbiOutFile(os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial))))
        TrthScore = LineG.calculateLogScore(TrueLabel)
        VitbScote = LineG.calculateLogScore(ViterbiLabel)
        TruthLabelScores.append(TrthScore)
        ViterbiLabelScores.append(VitbScote)
        if TrthScore/VitbScote <= 0.75:
            print serial
    plt.plot(TruthLabelScores, ViterbiLabelScores, 'ro')
    plt.xlabel('Truth Label Score')
    plt.ylabel('Viterbi Label Score')
    mm = max([max(TruthLabelScores), max(ViterbiLabelScores)])
    plt.xlim([0,mm + 1])
    plt.ylim([0,mm +1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.plot([0, mm], [0,mm], color='green')


    #plt.plot(np.unique(TruthLabelScores), np.poly1d(np.polyfit(TruthLabelScores, ViterbiLabelScores, 1))(np.unique(TruthLabelScores)))
    #results = sm.OLS(TruthLabelScores, sm.add_constant(ViterbiLabelScores)).fit()
    #print results.summary()
    #X_plot = np.linspace(0, 1, mm)
    #plt.plot(X_plot, X_plot * results.params[0] + results.params[1], color='blue')
    plt.show()
