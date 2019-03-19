from PathAndDir import Dir2ClusterGraph, Path2SelectedSerial, Dir2SelectedDynDomEntry
from Graph_Util_Funcs import ConstructRealClusterGraph
import cPickle as pickle
from Graph_Config import List_Colors, CutOffContact, Path2ViterbiJar, G_ConstructType
import os, sys
import numpy as np
import concurrent.futures
import igraph as ig
from AssistantObjects import DynDomEntry

def do_work(serial):
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
    G = ConstructRealClusterGraph(Entry.DistanceMatrices, Entry.Membership,
                              Construct_Type=G_ConstructType, cut_off_threshold=CutOffContact)
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)

    #idx = [v.index for v in G.vs if v['TrueLabel'] == 1 or v['TrueLabel'] == 3]
    #G = G.subgraph(idx)

    G.vs['color'] = [List_Colors[v['TrueLabel']] for v in G.vs]
    G['DynDomEntry'] = Entry
    G['SquareMatFeature'] = SquareMatFeature
    G.vs['OriginalIndex'] = [v.index for v in G.vs]
    G.es['OriginalIndex'] = [e.index for e in G.es]
    #ig.plot(G)

    #idxs = [v.index for v in G.vs if v['TrueLabel']!=3]
    #G = G.subgraph(idxs)
    #G['SquareMatFeature'] = G.calc_squareMatFeature(Entry.DistanceMatrices)

    Path2GraphFile = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    G.write_picklez(Path2GraphFile)
    return serial
if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [1479]
    # for serial in L:
    #     Path2GraphFile = os.path.join(Dir2PerfectGraph, '{}.pkl'.format(serial))
    #     G = ig.Graph().Read_Picklez(Path2GraphFile)
    #     print 'Num mistake: {}'.format(str(G.num_mistake()))
    #     #ig.plot(G)
    # sys.exit(1)
    #L = [559]

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
