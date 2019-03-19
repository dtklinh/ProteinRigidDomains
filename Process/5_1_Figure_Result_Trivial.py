from PathAndDir import Dir2ClusterGraph, Dir2ViterbiOutFile, Dir2Figure_Result_Trivial, Path2SelectedSerial
import igraph as ig
from igraph import BoundingBox, Plot
import os
from MyIO import ReadViterbiOutFile
import numpy as np
import concurrent.futures

def do_work(serial):
    G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
    EdgeLabel = ReadViterbiOutFile(os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial))))
    G.vs['size'] = [len(V['Cluster']) for V in G.vs]
    G.es['label'] = [E.index for E in G.es]
    G.es['width'] = [np.sqrt(E['Connectivity']) for E in G.es]
    G.es['color'] = [(0, 0, 0, 0.5) for E in G.es]
    edge_deleted_id = [idx for idx, val in enumerate(EdgeLabel)]

    Cls = G.merge(1, edge_deleted_id)
    Edge_final_removed_idx = []
    for E in G.es:
        v1_idx, v2_idx = E.source, E.target
        flag = False
        for C in Cls:
            if v1_idx in C and v2_idx in C:
                flag = True
                break
        if flag == False:
            Edge_final_removed_idx.append(E.index)
    G.delete_edges(Edge_final_removed_idx)
    bbox = BoundingBox(800, 800)
    figure = Plot(bbox=bbox, background='white')
    bbox = bbox.contract(20)
    figure.add(G, bbox=bbox, layout=G.layout("kamada_kawai"))
    # figure.show()
    figure.save(os.path.join(Dir2Figure_Result_Trivial, '{}.png'.format(str(serial))))

if __name__=='__main__':
    #done_serials = [int(f.split('.')[0]) for f in os.listdir(Dir2Figure_Result)]
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [i for i in L if i not in done_serials]
    #print L
    #L = [2661]

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

