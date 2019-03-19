from PathAndDir import Path2SelectedSerial, Dir2ClusterGraph, Dir2LineGraph
import numpy as np
import igraph as ig
import os, math, sys
from AssistantObjects import Feature_Workhouse
import matplotlib.pyplot as plt
from sklearn.preprocessing import QuantileTransformer, MinMaxScaler
from sklearn import metrics

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    L = [661]
    for serial in L:
        G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
        G.es['TrueLabel'] = [1 if G.vs[E.source]['TrueLabel'] == G.vs[E.target]['TrueLabel'] else -1 for E in G.es]
        LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
        # Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(serial))), 'rb'))
        Entry = G['DynDomEntry']
        Feature_Gen = Feature_Workhouse(Entry.DistanceMatrices)
        Arr_Ver = [[E.index, E.index, E['TrueLabel'],Feature_Gen.getMeanVar(G.vs[E.source]['Cluster'], G.vs[E.target]['Cluster'])] for E in G.es]
        Arr_Edge = [[E1.index, E2.index, 2 if G.vs[G.get_TwoEndNode(E1.index, E2.index)[0]]['TrueLabel'] == G.vs[G.get_TwoEndNode(E1.index, E2.index)[1]][
                'TrueLabel'] else -2, Feature_Gen.getMeanVar(G.vs[G.get_TwoEndNode(E1.index, E2.index)[0]]['Cluster'],
                 G.vs[G.get_TwoEndNode(E1.index, E2.index)[1]]['Cluster'])]
                    for E1 in G.es for E2 in G.es if E1.index < E2.index and G.isEdgeTouch(E1.index, E2.index) == 2]
        M = np.zeros((0, 4)).astype('object')
        M = np.append(M, np.matrix(Arr_Ver), 0)
        M = np.append(M, np.matrix(Arr_Edge), 0)
        M[:, 0:3] = M[:, 0:3].astype('i')
        M[:, 3] = M[:, 3].astype('float')
        Mx = np.zeros((len(G.es), len(G.es)))
        #print Mx.shape
        for i in range(M.shape[0]):
            #print M[i,0], M[i,1], M[i,3]
            Mx[M[i,0], M[i,1]] = M[i,3]
        Arr1, Arr2 = [], []
        for E in LineG.es:
            #print LineG.vs[E.source]['TrueLabel'], LineG.vs[E.target]['TrueLabel']
            if E["TwoEndNodeConnected"] is False:
                if LineG.vs[E.source]['TrueLabel'] == LineG.vs[E.target]['TrueLabel']:
                    val = Mx[E.source, E.source]/Mx[E.target, E.target] if Mx[E.source, E.source] > Mx[E.target, E.target] else Mx[E.target, E.target]/Mx[E.source, E.source]
                    val = math.log(val)
                    Arr1.append(val)
                else:
                    val = Mx[E.source, E.source] / Mx[E.target, E.target] if Mx[E.source, E.source] > Mx[E.target, E.target] else Mx[E.target, E.target] / Mx[E.source, E.source]
                    val = math.log(val)
                    Arr2.append(val)
                    #Arr2.append(Mx[E.source, E.target])

        y = [1]*len(Arr1) + [0]*len(Arr2)
        pred = Arr1 + Arr2
        print len(y)
        print len(pred)
        fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=0)
        print metrics.auc(fpr, tpr)
        '''
        MMScaler = MinMaxScaler(feature_range=(0,1))
        Arr = Arr1[:]
        Arr.extend(Arr2)
        Arr = np.matrix(Arr).transpose()
        #Arr1 = np.matrix(Arr1).transpose()
        #Arr2 = np.matrix(Arr2).transpose()
        MMScaler.fit(Arr)
        Arr = MMScaler.transform(Arr)
        #Arr1 = MMScaler.transform(Arr1)
        #Arr2 = MMScaler.transform(Arr2)
        print Arr
        plt.hist(Arr[0:len(Arr1)], np.arange(0,1,0.05), density=False, color='red', alpha=0.55)
        plt.hist(Arr[len(Arr1):], np.arange(0,1,0.05), density=False, color='blue', alpha=0.55)
        plt.show() '''
