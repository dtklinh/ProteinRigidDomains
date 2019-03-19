import numpy as np
import cPickle as pickle
import os, sys
from Graph_Util_Funcs import ConstructPerfectGraph, ConstructGraph
import igraph as ig
from FindNonRedundantScript import DynDomEntry
from GraphLibrary import D_Graph, D_LineGraph
from Graph_Config import List_Colors, Path2ViterbiJar
import concurrent.futures
from MyIO import ReadViterbiOutFile, WriteList2File
import matplotlib.pyplot as plt
from Evaluation_funcs import error_MemMershipMatrix, overlap

def do_work(serial):
    Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial))))
    G.vs['size'] = [len(V['Cluster']) for V in G.vs]
    G.es['label'] = [E.index for E in G.es]
    # ig.plot(G)
    # sys.exit()
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
    N_LineG, eds_LineG = G.constructLineGraph()
    LineG = D_LineGraph(G, N_LineG, eds_LineG)
    # LineG.setFeature(SquareMatFeature)

    Arr1 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] == G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    Arr2 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if
            G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] != G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
    return (float(len(Arr2)) / (len(Arr1) + len(Arr2)))

def do_work_Viterbi_LineG(serial):
    Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial))))
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
    N_LineG, eds_LineG = G.constructLineGraph()
    LineG = D_LineGraph(G, N_LineG, eds_LineG)
    LineG.setFeature(SquareMatFeature)
    Path2ViterbiFeature = os.path.join(Dir2ViterbiFeature, '{}.txt'.format(str(serial)))
    LineG.WriteFeature(Path2ViterbiFeature)
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    LineG.runViterbi(Path2ViterbiJar, Path2ViterbiFeature, Path2ViterbiOutFile)
    return serial
def do_work_Eval_Error_Overlap(serial):
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)
    G = ig.Graph()
    G = G.Read_Picklez(os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial))))
    deleted_ed_ids = [idx for idx, val in enumerate(PredLabels_Edges) if val==0]
    G.delete_edges(deleted_ed_ids)
    Membership = [v['TrueLabel'] for v in G.vs]
    Clsts = G.clusters()
    PredLabels = [-1]*len(Membership)
    for idx, c in enumerate(Clsts):
        for v_id in c:
            PredLabels[v_id] = idx
    assert sum([1 for i in PredLabels if i <0]) == 0
    error = error_MemMershipMatrix(Membership, PredLabels)
    ovlp = overlap(Membership, PredLabels)
    Lines = ['Error\t {}'.format(str(error)), 'Overlap\t {}'.format(str(ovlp))]
    Path2ResultFile = os.path.join(Dir2Result, '{}.txt'.format(str(serial)))
    WriteList2File(Path2ResultFile, Lines)
    return error, ovlp

if __name__=='__main__':
    Dir2SelectedDynDomEntry = '../MyDataSet/DynDom/SelectedDynDomEntry'
    Path2SelectedSerial = '../MyDataSet/DynDom/SerialList.txt'
    Dir2SelectedEntryFinal = '../MyDataSet/DynDom/SelectedEntryFinal'

    Dir2PerfectGraph        = '../MyDataSet/DynDom/Perfect/Graph'
    Dir2ViterbiFeature         = '../MyDataSet/DynDom/Perfect/ViterbiFeature'
    Dir2ViterbiOutFile      = '../MyDataSet/DynDom/Perfect/ViterbiOutFile'
    Dir2GraphFigure         = '../MyDataSet/DynDom/Perfect/Figure'
    Dir2Result              = '../MyDataSet/DynDom/Perfect/Result'

    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #done_serials = [int(f.split('.')[0]) for f in os.listdir(Dir2ViterbiOutFile) if os.path.isfile(os.path.join(Dir2ViterbiOutFile,f))]
    #L_left = [i for i in set(L) - set(done_serials)]

    #L = L[0:8]
    Arr_Err, Arr_Overlap = [], []
    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work_Eval_Error_Overlap, serial) for serial in L]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            Arr_Err.append(val[0])
            Arr_Overlap.append(val[1])
            print 'Finish: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()
    fig, ax = plt.subplots(1,2, figsize=(8,4))
    print Arr_Err
    print Arr_Overlap
    ax[0].hist(Arr_Err, bins=np.arange(0,1,0.01))
    ax[0].set_title('Histogram of Error')
    ax[0].set_xlabel('Error')
    ax[0].set_ylabel('Frequency')
    ax[1].hist(Arr_Overlap, bins=np.arange(0,1,0.01))
    ax[1].set_title('Histogram of Overlap')
    ax[1].set_xlabel('Overlap')
    ax[1].set_ylabel('Frequency')
    plt.savefig('../MyDataSet/DynDom/Perfect/Result_Histogram.png')
    plt.show()

    if False:
        Arr = []
        with concurrent.futures.ProcessPoolExecutor(8) as executor:
            futures_to_work = [executor.submit(do_work, serial) for serial in L]
            concurrent.futures.wait(futures_to_work)
        for future in concurrent.futures.as_completed(futures_to_work):
            try:
                val = future.result()
                Arr.append(val)
                print 'Finish serial: {}'.format(str(val))
            except:
                print "Error!!!"
        plt.hist(Arr, bins=np.arange(0,1,0.01))
        plt.xlabel('percent of across edge')
        plt.ylabel('frequency')
        plt.title('histogram of cross-edge of Line Graph')
        plt.savefig('../MyDataSet/DynDom/Perfect/Freq_CrossEdge_LineG.png')
        plt.show()


    '''
    TmpArr = []
    for serial in L:
        #if serial !=58: continue
        Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
        G = ig.Graph()
        G = G.Read_Picklez(os.path.join(Dir2PerfectGraph, '{}.pkl'.format(str(serial))))
        G.vs['size'] = [len(V['Cluster']) for V in G.vs]
        G.es['label'] = [E.index for E in G.es]
        #out = ig.plot(G)

        #sys.exit()
        SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
        N_LineG, eds_LineG = G.constructLineGraph()
        LineG = D_LineGraph(G, N_LineG, eds_LineG)
        LineG.setFeature(SquareMatFeature)

        #Arr1 = [SquareMatFeature[G.es[V.index].source, G.es[V.index].target] for V in LineG.vs if V['TrueLabel'] == 1]
        #Arr2 = [SquareMatFeature[G.es[V.index].source, G.es[V.index].target] for V in LineG.vs if V['TrueLabel'] != 1]
        Arr1 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] == G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
        Arr2 = [SquareMatFeature[E['TwoEndNodes_ID'][0], E['TwoEndNodes_ID'][1]] for E in LineG.es if G.vs[E['TwoEndNodes_ID'][0]]['TrueLabel'] != G.vs[E['TwoEndNodes_ID'][1]]['TrueLabel']]
        plt.hist(Arr1, bins = np.arange(0,10,0.1), alpha=0.55, color='red')
        plt.hist(Arr2, bins=50, alpha=0.55, color='blue')
        plt.show()
        from HistogramUtils import plotHistogramQuanTrans
        plotHistogramQuanTrans(Arr1, Arr2)
        #TmpArr.append(float(len(Arr2))/(len(Arr1) + len(Arr2)))
        #continue

        Path2ViterbiFeature = os.path.join(Dir2ViterbiFeature, '{}.txt'.format(str(serial)))
        LineG.WriteFeature(Path2ViterbiFeature)
        Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
        LineG.runViterbi(Path2ViterbiJar, Path2ViterbiFeature, Path2ViterbiOutFile)


        ViterbiLabel = ReadViterbiOutFile(Path2ViterbiOutFile)
        DeletedEds_ID = [idx for idx, val in enumerate(ViterbiLabel) if val ==0]
        G.delete_edges(DeletedEds_ID)
        ig.plot(G)
        TrueLabel = LineG.vs['TrueLabel']
        print 'Score for True Label: {}'.format(str(LineG.calculateLogScore(TrueLabel)))
        print 'Score for Viterbi label: {}'.format(str(LineG.calculateLogScore(ViterbiLabel)))
    '''