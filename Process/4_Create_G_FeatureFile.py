from PathAndDir import Dir2G_Feature, Dir2ClusterGraph, Dir2SelectedDynDomEntry, Path2SelectedSerial
import igraph as ig
import os
from AssistantObjects import DynDomEntry, Feature_Workhouse
import cPickle as pickle
import numpy as np
import concurrent.futures
from sklearn.preprocessing import QuantileTransformer

def do_work(serial):
    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    G.es['TrueLabel'] = [1 if G.vs[E.source]['TrueLabel']==G.vs[E.target]['TrueLabel'] else -1 for E in G.es]
    #Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(serial))), 'rb'))
    Entry = G['DynDomEntry']
    Feature_Gen = Feature_Workhouse(Entry.DistanceMatrices)
    Arr_Ver = [[E.index, E.index, E['TrueLabel'], Feature_Gen.getMeanVar(G.vs[E.source]['Cluster'], G.vs[E.target]['Cluster'])] for E in G.es]
    Arr_Edge = [[E1.index, E2.index, 2 if
        G.vs[G.get_TwoEndNode(E1.index, E2.index)[0]]['TrueLabel']==G.vs[G.get_TwoEndNode(E1.index, E2.index)[1]]['TrueLabel'] else -2,
         Feature_Gen.getMeanVar(G.vs[G.get_TwoEndNode(E1.index, E2.index)[0]]['Cluster'], G.vs[G.get_TwoEndNode(E1.index, E2.index)[1]]['Cluster'])]
        for E1 in G.es for E2 in G.es if E1.index < E2.index and G.isEdgeTouch(E1.index, E2.index)==2]
    M = np.zeros((0,4)).astype('object')
    M = np.append(M, np.matrix(Arr_Ver), 0)
    M = np.append(M, np.matrix(Arr_Edge), 0)
    M[:,0:3] = M[:,0:3].astype('i')
    M[:,3] = M[:,3].astype('float')
    #M_ver = M[np.logical_or.reduce([M[:,2] == x for x in (1, -1)]), :]
    #M_ed = M[np.logical_or.reduce([M[:,2] == x for x in (2, -2)]), :] #M[M[:,2]==2 or M[:,2]==-2,:]
    #print M[0:3,:]
    #scaler_ver  = QuantileTransformer().fit(M_ver)

    np.savetxt(os.path.join(Dir2G_Feature, '{}.txt'.format(str(serial))), M, fmt='%i %i %i %f')

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    L = [2661]

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