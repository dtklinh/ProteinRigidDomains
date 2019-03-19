import os, concurrent.futures
import igraph as ig
import numpy as np
from PathAndDir import Dir2ClusterGraph, Dir2Result_Cluster, Dir2Membership, Path2SelectedSerial
from MyIO import ReadLines, WriteList2File



def do_work(serial):
    Path2Result_Cluster = os.path.join(Dir2Result_Cluster, '{}.txt'.format(str(serial)))
    Lines = ReadLines(Path2Result_Cluster)
    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    Entry = G['DynDomEntry']
    Membership = Entry.Membership
    BestPossibleLabel = [-1]*len(Membership)
    for v in G.vs:
        for i in v['Cluster']:
            BestPossibleLabel[i] = v['TrueLabel']
    assert sum([1 for i in BestPossibleLabel if i < 0]) == 0

    PredLabel         = [-1]*len(Membership)
    for idx, line in enumerate(Lines):
        Arr = line.split()
        Arr = map(int, Arr)
        for v_id in Arr:
            for i in G.vs[v_id]['Cluster']:
                PredLabel[i] = idx
    assert sum([1 for i in PredLabel if i < 0]) == 0

    Arr_Out = []
    Arr_Out.append('\t'.join([str(i) for i in Membership]))
    #Arr_Out.append('\t'.join([str(i) for i in BestPossibleLabel]))
    Arr_Out.append('\t'.join([str(i) for i in PredLabel]))
    WriteList2File(os.path.join(Dir2Membership, '{}.txt'.format(str(serial))), Arr_Out)
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
