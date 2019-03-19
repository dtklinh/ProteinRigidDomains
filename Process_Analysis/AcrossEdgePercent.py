from PathAndDir import *
from GraphLibrary import D_LineGraph
import os
import igraph as ig
from AssistantObjects import DynDomEntry
import cPickle as pickle
import numpy as np
import concurrent.futures
import matplotlib.pyplot as plt

def do_work(serial):
    Path2DynDomEntryFile = os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(serial)))
    Entry = pickle.load(open(Path2DynDomEntryFile, 'rb'))

    Path2LineGraphFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    LineG = ig.Graph().Read_Picklez(Path2LineGraphFile)

    Path2GraphFile = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    G = ig.Graph().Read_Picklez(Path2GraphFile)

    #N_LineG, eds_LineG = G.constructLineGraph()
    #LineG = D_LineGraph(G, N_LineG, eds_LineG)

    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)

    Arr1 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] == G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    Arr2 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] != G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    return (float(len(Arr2)) / (len(Arr1) + len(Arr2)))

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    Arr = []
    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work, serial) for serial in L[0:1]]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            Arr.append(val)
            print 'Finish serial: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()
    plt.hist(Arr, bins = np.arange(0,1,0.01))
    plt.show()