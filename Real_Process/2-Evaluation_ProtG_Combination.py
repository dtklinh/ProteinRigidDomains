from PathAndDir import *
from GraphLibrary import D_Graph
from Evaluation_funcs import overlap, error_MemMershipMatrix
from MyIO import ReadViterbiOutFile, WriteList2File
import igraph as ig
import numpy as np
import os
import concurrent.futures
import matplotlib.pyplot as plt

def do_work(serial):
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    Entry = G['DynDomEntry']

    Pair_idx_ToBeRemoved = [(G.es[idx].source, G.es[idx].target) for idx, val in enumerate(PredLabels_Edges) if val == 0]
    Pair_idx_ToBeRemoved_2 = [(G.es[idx].source, G.es[idx].target) for idx, val in enumerate(PredLabels_Edges)]

    #G.delete_edges(Pair_idx_ToBeRemoved)
    #Clsts = G.merge(1.0, Pair_idx_ToBeRemoved)
    #print G.clusters()

    Membership = Entry.Membership
    #Clsts = G1.clusters()
    def make_pred_label(Pair_idx_Removed):
        Clsts = G.merge(1.0, Pair_idx_Removed)
        PredLabels = [-1] * len(Membership)
        for idx, c in enumerate(Clsts):
            for v_id in c:
                for i in G.vs[v_id]['Cluster']:
                    PredLabels[i] = idx
        return PredLabels

    PredLabels_1 = make_pred_label(Pair_idx_ToBeRemoved)
    PredLabels_2 = make_pred_label(Pair_idx_ToBeRemoved_2)
    assert sum([1 for i in PredLabels_1 if i < 0]) == 0
    error = min(error_MemMershipMatrix(Membership, PredLabels_1), error_MemMershipMatrix(Membership, PredLabels_2))
    ovlp = max(overlap(Membership, PredLabels_1), overlap(Membership, PredLabels_2))
    #Lines = ['Error\t {}'.format(str(error)), 'Overlap\t {}'.format(str(ovlp))]
    #Path2ResultFile = os.path.join(Dir2Result, '{}.txt'.format(str(serial)))
    #WriteList2File(Path2ResultFile, Lines)
    print serial, error, ovlp
    return serial, error, ovlp

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [564]
    #L = [int(f.split('.')[0]) for f in os.listdir(Dir2LineGraph)]
    print L
    Arr_Error = []
    Arr_Overlap = []

    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work, serial) for serial in L]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            Arr_Error.append(val[1])
            Arr_Overlap.append(val[2])
            print 'Finish: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()
    fig, ax = plt.subplots(1,2, figsize=(8,4))
    print "AVERAGE ERROR: {}".format(str(np.mean(Arr_Error)))
    print "AVERAGE OVERLAP: {}".format(str(np.mean(Arr_Overlap)))
    print Arr_Error
    print Arr_Overlap
    ax[0].hist(Arr_Error, bins=np.arange(0,1,0.01))
    ax[0].set_title('Histogram of Error')
    ax[0].set_xlabel('Error')
    ax[0].set_ylabel('Frequency')
    ax[1].hist(Arr_Overlap, bins=np.arange(0,1,0.01))
    ax[1].set_title('Histogram of Overlap')
    ax[1].set_xlabel('Overlap')
    ax[1].set_ylabel('Frequency')
    plt.savefig('../MyDataSet/DynDom/Perfect/Result_Histogram_10.5.png')
    plt.show()

