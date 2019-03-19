# Complete procudure
# Input: serial of protein
# Output: Idx of cluster

import igraph as ig
import numpy as np
import matplotlib.pyplot as plt
import os, concurrent.futures, time
from PathAndDir import Dir2ClusterGraph, Path2SelectedSerial, Dir2Result_Cluster
from Evaluation_funcs import overlap, error_MemMershipMatrix
from MyIO import WriteList2File

def do_work(serial):
    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    G['serial'] = serial
    #idx = [v.index for v in G.vs if v['TrueLabel']==1 or v['TrueLabel']==3]
    #G = G.subgraph(idx)
    Entry = G['DynDomEntry']
    Membership = Entry.Membership

    G_Org_Indexs = [i for v in G.vs for i in v['Cluster']]
    delete_indexs = [i for i in range(len(Membership)) if i not in G_Org_Indexs]
    Membership = [i for j, i in enumerate(Membership) if j not in delete_indexs]

    Arr = G.do_work_iteration(rmsd_thres = 3.5)
    #Arr = [G.subgraph(v.index) for v in G.vs]
    #Arr = G.do_merge(1.0, Arr)
    PredLabels = [-1] * len(Membership)
    for idx, c in enumerate(Arr):
        for v in c.vs:
            for i in v['Cluster']:
                PredLabels[i] = idx
    PredLabels = [i for j, i in enumerate(PredLabels) if j not in delete_indexs]
    assert sum([1 for i in PredLabels if i < 0]) == 0
    error = error_MemMershipMatrix(Membership, PredLabels)
    ovlp = overlap(Membership, PredLabels)
    return serial, error, ovlp, Arr

if __name__=='__main__':
    t_start = time.time()
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #serial = 559

    Arr_Error = []
    Arr_Overlap = []
    Arr_Out = []
    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work, serial) for serial in L]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            # Path2Result_Cluster = os.path.join(Dir2Result_Cluster, '{}.txt'.format(str(val[0])))
            # tmp_Arr = []
            # for G in val[3]:
            #     line = '\t'.join([str(v['OriginalIndex']) for v in G.vs])
            #     tmp_Arr.append(line)
            # print 'SSS'
            # print tmp_Arr
            # WriteList2File(Path2Result_Cluster, tmp_Arr)

            Arr_Error.append(val[1])
            Arr_Overlap.append(val[2])
            Arr_Out.append('{}\t{}\t{}'.format(str(val[0]), str(val[1]), str(val[2])))
            print 'Finish: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()

    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    print "AVERAGE ERROR: {}".format(str(np.mean(Arr_Error)))
    print "AVERAGE OVERLAP: {}".format(str(np.mean(Arr_Overlap)))
    print '------------------------'
    print "MEDIAN ERROR: {}".format(str(np.median(Arr_Error)))
    print "MEDIAN OVERLAP: {}".format(str(np.median(Arr_Overlap)))
    print Arr_Error
    print Arr_Overlap
    ax[0].hist(Arr_Error, bins=np.arange(0, 1, 0.01))
    ax[0].set_title('Histogram of Error')
    ax[0].set_xlabel('Error')
    ax[0].set_ylabel('Frequency')
    ax[1].hist(Arr_Overlap, bins=np.arange(0, 1.01, 0.01))
    ax[1].set_title('Histogram of Overlap')
    ax[1].set_xlabel('Overlap')
    ax[1].set_ylabel('Frequency')
    plt.savefig('../MyDataSet/DynDom/Perfect/Result_Histogram_10.5_withoutMerge.png')
    WriteList2File('../MyDataSet/DynDom/Real/Result_WithoutMerge.txt', Arr_Out)
    t_end = time.time()
    print 'Esclaped time is {}'.format(str(t_end-t_start))
    plt.show()
    '''
    Arr, err, ovlp = do_work(serial)
    for idx, G in enumerate(Arr):
        Cluaters = [v['Cluster'] for v in G.vs]
        print len(G.vs)
        print Cluaters
        print "RMSD: {}".format(str(G.rmsd()))
        print 'Error: {}'.format(str(err))
        print 'Overlap: {}'.format(str(ovlp))
        ig.plot(G)  '''