from PathAndDir import Dir2SelectedDynDomEntry, Path2SelectedSerial
from Graph_Util_Funcs import ConstructGraph
from GraphLibrary import D_LineGraph
from Graph_Config import List_Colors
import cPickle as pickle
import os, concurrent.futures
import numpy as np


def do_work(serial):
    Dir2LineGraph = '../MyDataSet/DynDom/AUC/ProteinG'
    Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))
    Membership = Entry.Membership
    G = ConstructGraph(Entry.DistanceMatrices, Construct_Type=2, cut_off_threshold=7.5, Membership=Membership)
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
    G.vs['color'] = [List_Colors[v['TrueLabel']] for v in G.vs]
    G['DynDomEntry'] = Entry
    G['SquareMatFeature'] = SquareMatFeature
    G.vs['OriginalIndex'] = [v.index for v in G.vs]
    G.es['OriginalIndex'] = [e.index for e in G.es]

    #N_LineG, eds_LineG = G.constructLineGraph(ConsiderTwoEndNodesConn=True)
    #LineG = D_LineGraph(N_LineG, eds_LineG, graph_attrs={'OriginalGraph': G, 'SquareMatFeature': SquareMatFeature})
    #LineG.setFeature_Sim(SquareMatFeature, 4, 8)
    Path2LineGFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    G.write_picklez(Path2LineGFile, pickle.HIGHEST_PROTOCOL)


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

