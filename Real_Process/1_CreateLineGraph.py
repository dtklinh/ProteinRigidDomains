from PathAndDir import Dir2SelectedDynDomEntry, Dir2ClusterGraph, Dir2LineGraph, Dir2ViterbiFeature, Dir2ViterbiOutFile, Path2SelectedSerial
import numpy as np
import igraph as ig
import cPickle as pickle
import os, sys
from AssistantObjects import DynDomEntry
from GraphLibrary import D_Graph, D_LineGraph
from Graph_Config import Path2ViterbiJar
import concurrent.futures

def do_work(serial):
    #Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))

    #idx = [v.index for v in G.vs if v['TrueLabel'] == 1 or v['TrueLabel'] == 3]
    #G = G.subgraph(idx)

    #Entry = G['DynDomEntry']
    SquareMatFeature = G['SquareMatFeature'] #.calc_squareMatFeature(Entry.DistanceMatrices)
    N_LineG, eds_LineG = G.constructLineGraph()
    LineG = D_LineGraph(N_LineG, eds_LineG, graph_attrs={'OriginalGraph':G, 'SquareMatFeature':SquareMatFeature})
    #LineG.initial()
    #LineG.setFeature(SquareMatFeature)
    LineG.setFeature_Sim(SquareMatFeature, 4, 8)
    Path2LineGFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    LineG.write_picklez(Path2LineGFile, pickle.HIGHEST_PROTOCOL)

    Path2ViterbiFeature = os.path.join(Dir2ViterbiFeature, '{}.txt'.format(str(serial)))
    LineG.WriteFeature(Path2ViterbiFeature)
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    LineG.runViterbi(Path2ViterbiJar, Path2ViterbiFeature, Path2ViterbiOutFile)
    return serial

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [559]


    #done_serials = [int(f.split('.')[0]) for f in os.listdir(Dir2LineGraph)]
    #L_left = [i for i in set(L) - set(done_serials)]
    #print len(L_left)

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