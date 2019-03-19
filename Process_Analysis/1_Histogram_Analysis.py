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
from Outlier_Detection.Config import Vertex_outlier_Thres, Edge_outlier_Thres
from Outlier_Detection.OutlierLib import is_outlier
from HistogramUtils import plotHistogramQuanTrans2

def do_work(serial):
    LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
    G = LineG['OriginalGraph']

    #idx = [v.index for v in G.vs if v['TrueLabel'] == 1 or v['TrueLabel'] == 3]
    #G = G.subgraph(idx)

    SquareMatFeature = LineG['SquareMatFeature']

    Arr_Edge = [SquareMatFeature[0, e["TwoEndNodes_ID"][0], e["TwoEndNodes_ID"][1]] for e in LineG.es if
            e["TwoEndNodeConnected"] == False]
    Arr_Ver = [SquareMatFeature[0,e.source, e.target] for e in G.es]
    Arr_Edge = np.array(Arr_Edge)
    Arr_Ver = np.array(Arr_Ver)

    Vertex_IsOut = is_outlier(Arr_Ver, Vertex_outlier_Thres)
    Edge_IsOut   = is_outlier(Arr_Edge, Edge_outlier_Thres)

    Arr_Ver_Label = [1 if G.vs[e.source]['TrueLabel']==G.vs[e.target]['TrueLabel'] else -1 for e in G.es]
    Arr_Edge_Label = [1 if G.vs[e["TwoEndNodes_ID"][0]]['TrueLabel'] == G.vs[e["TwoEndNodes_ID"][1]]['TrueLabel'] else -1 for e in
         LineG.es if e["TwoEndNodeConnected"] == False]
    plotHistogramQuanTrans2(serial, Arr_Ver, Arr_Ver_Label, Vertex_IsOut, Arr_Edge, Arr_Edge_Label, Edge_IsOut)


if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    L = [559]
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