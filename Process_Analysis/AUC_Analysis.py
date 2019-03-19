#-- we analyze feature through AUC
from PathAndDir import Path2SelectedSerial, Dir2LineGraph
import numpy as np
import igraph as ig
import os, random, math, concurrent.futures
from sklearn import metrics
import matplotlib.pyplot as plt

def do_work_vertex(serial):
    LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
    G = LineG['OriginalGraph']
    SquareMatFeature = LineG['SquareMatFeature']
    pred = []
    y = []
    num_within, num_across = 0, 0
    for e in G.es:
        v1_idx, v2_idx = e.source, e.target
        if G.vs[v1_idx]['TrueLabel'] == G.vs[v2_idx]['TrueLabel']:
            y.append(0)
            num_within += 1
        else:
            y.append(1)
            num_across += 1
        pred.append(SquareMatFeature[0, v1_idx, v2_idx])
        # pred.append(random.random())
    if len(set(y))==1:
        return serial, np.NaN
    fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
    ratio = float(num_within) / num_across if num_across != 0 else 'Inf'
    auc = metrics.auc(fpr, tpr)
    return serial, auc
def do_work_edge(serial):
    LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
    G = LineG['OriginalGraph']
    SquareMatFeature = LineG['SquareMatFeature']
    pred = []
    y = []
    num_within, num_across = 0, 0
    G.es['TrueLabel'] = [0 if G.vs[e.source]['TrueLabel'] == G.vs[e.target]['TrueLabel'] else 1 for e in G.es]
    num_within, num_across = 0, 0
    for E in LineG.es:
        e1_idx, e2_idx = E.source, E.target
        v1_idx, v2_idx = E["TwoEndNodes_ID"]
        if E["TwoEndNodeConnected"] == False:
            if G.es[e1_idx]['TrueLabel'] == 0 and G.es[e2_idx]['TrueLabel'] == 0:
                y.append(0)
                num_within += 1
            else:
                y.append(1)
                num_across += 1
            pred.append(SquareMatFeature[0, v1_idx, v2_idx])
    if len(set(y))==1:
        return serial, np.NaN
    fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
    ratio = float(num_within) / num_across if num_across != 0 else 'Inf'
    auc = metrics.auc(fpr, tpr)
    return serial, auc
#-------------------------------------------------------------------------------------

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [661]
    #serial = L[0]

    AUC, Arr_Ratio = [], []

    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work_vertex, serial) for serial in L]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            if np.isnan(val[1])== False: AUC.append(val[1])
            print 'Finish serial: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()
    print 'Mean of AUC: {}'.format(str(np.mean(AUC)))
    print 'Median of AUC: {}'.format(str(np.median(AUC)))


    # check feature val of Vertex in LineGraph
    '''
    for serial in L:
        LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
        G = LineG['OriginalGraph']
        SquareMatFeature = LineG['SquareMatFeature']
        pred = []
        y = []
        num_within, num_across = 0, 0
        for e in G.es:
            v1_idx, v2_idx = e.source, e.target
            if G.vs[v1_idx]['TrueLabel'] == G.vs[v2_idx]['TrueLabel']:
                y.append(0)
                num_within += 1
            else:
                y.append(1)
                num_across += 1
            pred.append(SquareMatFeature[0,v1_idx, v2_idx])
            #pred.append(random.random())
        fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
        ratio = float(num_within)/num_across if num_across!= 0 else 'Inf'
        auc = metrics.auc(fpr, tpr)
        if np.isnan(auc) == False:
            AUC.append(auc)
            Arr_Ratio.append(ratio)
        print 'Serial: {} \t AUC: {} \t ratio(within/across): {}'.format(str(serial), str(auc), str(ratio))
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    print AUC
    print Arr_Ratio
    ax[0].hist(AUC, bins=np.arange(0,1,0.01))
    ax[0].set_xlabel('MeanVar_LineG_Vertex')
    ax[1].hist(Arr_Ratio)
    ax[1].set_xlabel('within/across')
    fig.tight_layout()
    plt.show() #'''

        #-- check feature val of Edge in LineGraph
    '''
    for serial in L:
        LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
        G = LineG['OriginalGraph']
        SquareMatFeature = LineG['SquareMatFeature']
        pred = []
        y = []
        num_within, num_across = 0, 0
        G.es['TrueLabel'] = [0 if G.vs[e.source]['TrueLabel'] == G.vs[e.target]['TrueLabel'] else 1 for e in G.es]
        num_within, num_across = 0, 0
        for E in LineG.es:
            e1_idx, e2_idx = E.source, E.target
            v1_idx, v2_idx = E["TwoEndNodes_ID"]
            if E["TwoEndNodeConnected"] == False:
                if G.es[e1_idx]['TrueLabel'] == 0 and G.es[e2_idx]['TrueLabel'] == 0:
                    y.append(0)
                    num_within += 1
                else:
                    y.append(1)
                    num_across +=1
                pred.append(SquareMatFeature[0, v1_idx, v2_idx])
        fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
        ratio = float(num_within) / num_across if num_across != 0 else 'Inf'
        auc = metrics.auc(fpr, tpr)
        if np.isnan(auc) == False:
            AUC.append(auc)
            Arr_Ratio.append(ratio)
        print 'Serial: {} \t AUC: {} \t ratio(within/across): {}'.format(str(serial), str(auc), str(ratio))
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    print AUC
    print Arr_Ratio
    ax[0].hist(AUC, bins=np.arange(0, 1, 0.01))
    ax[0].set_xlabel('MeanVar_LineG_Edge')
    ax[1].hist(Arr_Ratio)
    ax[1].set_xlabel('within/across')
    fig.tight_layout()
    plt.show() '''

    # Check
    '''
    for serial in L:
        LineG = ig.Graph().Read_Picklez(os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial))))
        G = LineG['OriginalGraph']
        SquareMatFeature = LineG['SquareMatFeature']
        pred = []
        y = []
        num_within, num_across = 0, 0
        G.es['TrueLabel'] = [0 if G.vs[e.source]['TrueLabel'] == G.vs[e.target]['TrueLabel'] else 1 for e in G.es]
        num_within, num_across = 0, 0
        for E in LineG.es:
            e1_idx, e2_idx = E.source, E.target
            v1_idx, v2_idx = E["TwoEndNodes_ID"]
            v_mid_idx = E["MidNode_ID"]
            if E["TwoEndNodeConnected"] == False:
                if G.es[e1_idx]['TrueLabel'] == 0 and G.es[e2_idx]['TrueLabel'] == 0:
                    y.append(0)
                    num_within += 1
                else:
                    y.append(1)
                    num_across += 1
                val = abs(SquareMatFeature[0,v_mid_idx,v1_idx] - SquareMatFeature[0,v_mid_idx, v2_idx])
                #val = SquareMatFeature[0,v_mid_idx,v1_idx]/ SquareMatFeature[0,v_mid_idx, v2_idx]
                #val = val if val > 1 else 1.0/val
                #val = math.log(val)
                pred.append(val)
        fpr, tpr, thresholds = metrics.roc_curve(y, pred, pos_label=1)
        ratio = float(num_within) / num_across if num_across != 0 else 'Inf'
        auc = metrics.auc(fpr, tpr)
        if np.isnan(auc) == False:
            AUC.append(auc)
            Arr_Ratio.append(ratio)
        print 'Serial: {} \t AUC: {} \t ratio(within/across): {}'.format(str(serial), str(auc), str(ratio))
    fig, ax = plt.subplots(1, 2, figsize=(8, 4))
    print AUC
    print Arr_Ratio
    ax[0].hist(AUC, bins=np.arange(0, 1, 0.01))
    ax[0].set_xlabel('MeanVar_LineG_Edge')
    ax[1].hist(Arr_Ratio)
    ax[1].set_xlabel('within/across')
    fig.tight_layout()
    plt.show() '''


