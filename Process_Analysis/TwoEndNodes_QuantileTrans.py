import igraph as ig
from PathAndDir import Dir2ClusterGraph, Path2SelectedSerial, Dir2SelectedDynDomEntry
import os
import numpy as np
from GraphLibrary import D_LineGraph
import cPickle as pickle
from AssistantObjects import DynDomEntry

def do_work(serial):
    return None

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    serial = L[0]

    Path2DynDomEntryFile = os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(serial)))
    Entry = pickle.load(open(Path2DynDomEntryFile, 'rb'))

    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))

    N_LineG, eds_LineG = G.constructLineGraph()
    LineG = D_LineGraph(G, N_LineG, eds_LineG)

    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)

    Arr1 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            E["TwoEndNodeConnected"]==False and G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] == G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    Arr2 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            E["TwoEndNodeConnected"] == False and G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] != G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    Arr1_VLG = [SquareMatFeature[G.es[V.index].source, G.es[V.index].target] for V in LineG.vs if V['TrueLabel'] == 1]
    Arr2_VLG = [SquareMatFeature[G.es[V.index].source, G.es[V.index].target] for V in LineG.vs if V['TrueLabel'] != 1]
    #plt.hist(Arr1, bins=np.arange(0, 10, 0.1), alpha=0.55, color='red')
    from HistogramUtils import plotHistogramQuanTrans
    Arr1_VLG.sort(reverse=True)
    Arr2_VLG.sort(reverse=True)
    print Arr1_VLG
    print Arr2_VLG

    plotHistogramQuanTrans(Arr1_VLG, Arr2_VLG)

