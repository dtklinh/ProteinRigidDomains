from PathAndDir import Dir2LineGraph, Dir2FeatureHistogram, Dir2SelectedDynDomEntry, Path2SelectedSerial, Dir2ClusterGraph
import matplotlib.pyplot as plt
import numpy as np
from AssistantObjects import DynDomEntry, Feature_Workhouse
from GraphLibrary import D_LineGraph, D_Graph
import os, sys
import igraph as ig
import cPickle as pickle
from HistogramUtils import plotHistogramQuanTrans
import concurrent.futures

def do_work(serial):
    Path2DynDomEntry = os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(serial)))
    #Entry = pickle.load(open(Path2DynDomEntry, 'rb'))
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    Entry = G['DynDomEntry']
    Mx = Entry.DistanceMatrices
    #Feature_Gen = Feature_Workhouse(Mx)
    Path2LineGraphFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    LineG = ig.Graph().Read_Picklez(Path2LineGraphFile)
    G = LineG['OriginalGraph']
    #SquareMatFeature = G.calc_squareMatFeature(Mx)
    SquareMatFeature = LineG['SquareMatFeature']

    #Arr_Ver = [(E.source, E.target, Feature_Workhouse.getMeanVar(G.vs[E.source][])) for E in G.es]

    Arr1 = [SquareMatFeature[0, E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            E["TwoEndNodeConnected"] == False and G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] ==
            G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    Arr2 = [SquareMatFeature[0, E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            E["TwoEndNodeConnected"] == False and G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] !=
            G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    plotHistogramQuanTrans(Arr1, Arr2, serial)

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    L = [911]
    #L = [int(f.split('.')[0]) for f in os.listdir(Dir2LineGraph)]
    print L
    # for serial in L:
    #     do_work(serial)
    #     sys.exit()

    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work, serial) for serial in L]
        #concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            print 'Finish serial: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()