from PathAndDir import *
from Graph_Util_Funcs import ConstructPerfectGraph
import cPickle as pickle
from Graph_Config import List_Colors, CutOffContact, Path2ViterbiJar, G_ConstructType
import os
import numpy as np
import concurrent.futures
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
    G = ConstructPerfectGraph(Entry.DistanceMatrices, Entry.Membership,
                              Construct_Type=G_ConstructType, cut_off_threshold=CutOffContact)
    SquareMatFeature = G.calc_squareMatFeature(Entry.DistanceMatrices)
    G['SquareMatFeature'] = SquareMatFeature
    G.vs['color'] = [List_Colors[v['TrueLabel']] for v in G.vs]
    G['DynDomEntry'] = Entry
    G.vs['OriginalIndex'] = [v.index for v in G.vs]
    G.es['OriginalIndex'] = [e.index for e in G.es]
    Path2GraphFile = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    G.write_picklez(Path2GraphFile)
    return serial
if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [1479]
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
