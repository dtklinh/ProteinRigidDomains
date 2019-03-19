import numpy as np
import cPickle as pickle
import os
from Graph_Util_Funcs import ConstructPerfectGraph, ConstructGraph
import igraph as ig
from FindNonRedundantScript import DynDomEntry
from GraphLibrary import D_Graph, D_LineGraph
from Graph_Config import List_Colors, Path2ViterbiJar
import concurrent.futures

def do_work_CreatePerfectGraph(serial):
    Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    # G = ConstructPerfectGraph(Entry.DistanceMatrices, Entry.Membership, Construct_Type=2, cut_off_threshold=7.5)
    Membership = Entry.Membership
    Set_Label = set(Membership)
    Total_Arr = []
    for l in Set_Label:
        Arr = [idx for idx, val in enumerate(Membership) if val == l]
        if len(Arr) < 10:
            Total_Arr.extend(Arr)
    Entry = Entry.trim(Total_Arr)
    G = ConstructPerfectGraph(Entry.DistanceMatrices, Entry.Membership, Construct_Type=2, cut_off_threshold=10.5)
    G.vs['color'] = [List_Colors[v['TrueLabel']] for v in G.vs]
    Path2GraphFile = os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial)))
    G.write_picklez(Path2GraphFile)
    return serial
#--------------------------------------------------
def do_work_LG_Viterbi(serial):
    Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial))))
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
    N_LineG, eds_LineG = G.constructLineGraph()
    LineG = D_LineGraph(G, N_LineG, eds_LineG)
    LineG.setFeature(SquareMatFeature)
    Path2ViterbiFeature = os.path(Dir2ViterbiFeature, '{}.txt'.format(str(serial)))
    LineG.WriteFeature(Path2ViterbiFeature)
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    LineG.runViterbi(Path2ViterbiJar, Path2ViterbiFeature, Path2ViterbiOutFile)
    return serial


if __name__=='__main__':
    Dir2SelectedDynDomEntry = '../MyDataSet/DynDom/SelectedDynDomEntry'
    Path2SelectedSerial = '../MyDataSet/DynDom/SerialList.txt'
    Dir2SelectedEntryFinal = '../MyDataSet/DynDom/SelectedEntryFinal'

    Dir2PerfectGraph        = '../MyDataSet/DynDom/Perfect/Graph'
    Dir2ViterbiFeature         = '../MyDataSet/DynDom/Perfect/ViterbiFeature'
    Dir2ViterbiOutFile      = '../MyDataSet/DynDom/Perfect/ViterbiOutFile'

    L = np.loadtxt(Path2SelectedSerial).astype('i')

    with concurrent.futures.ProcessPoolExecutor(1) as executor:
        futures_to_work = [executor.submit(do_work_LG_Viterbi, serial) for serial in L]
        #concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            print 'Finish serial: {}'.format(str(val))
        except:
            print "Error!!!"

'''
    for serial in L:
        Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
        #G = ConstructPerfectGraph(Entry.DistanceMatrices, Entry.Membership, Construct_Type=2, cut_off_threshold=7.5)
        Membership = Entry.Membership
        Set_Label = set(Membership)
        Total_Arr = []
        for l in Set_Label:
            Arr = [idx for idx, val in enumerate(Membership) if val == l]
            if len(Arr) < 10:
                Total_Arr.extend(Arr)
        Entry = Entry.trim(Total_Arr)
        G = ConstructPerfectGraph(Entry.DistanceMatrices,Entry.Membership, Construct_Type=2, cut_off_threshold=7.5)
        G.vs['color'] = [List_Colors[v['TrueLabel']] for v in G.vs]
        Path2GraphFile = os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial)))
        G.write_picklez(Path2GraphFile)
        G2 = ig.Graph()
        G2 = G2.Read_Picklez(Path2GraphFile)
        ig.plot(G2)
        print type(G2)
        '''
        #pickle.dump(G, open(Path2GraphFile, 'wb'), pickle.HIGHEST_PROTOCOL)

        #out = ig.plot(G)
        #out.save(os.path.join(Dir2GraphFigure, '{}.png'.format(str(serial))))

        #G2 = pickle.load(open(Path2GraphFile, 'rb'))
        #ig.plot(G2)