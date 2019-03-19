from FindNonRedundantScript import DynDomEntry
from AssistantObjects import Object_1, Object_2
from Evaluation_funcs import eval_error, eval_majority_error, random_Labels
import os, sys
import numpy as np
import cPickle as pickle
import matplotlib.pyplot as plt
import json

Dir2SelectedEntryFinal = '../MyDataSet/DynDom/SelectedEntryFinal'
Dir2DynDomEntry = '../MyDataSet/DynDom/SelectedDynDomEntry'
Dir2SelectedEntryFinal = '../MyDataSet/DynDom/SelectedEntryFinal'
Path2SelectedSerial = '../MyDataSet/DynDom/SerialList.txt'

#def do_work()

if __name__=='__main__':
    G_Construct_Types = [0, 2]
    #CutOffThresholds = np.arange(7,15, 0.5)
    CutOffThresholds = [7.5, 10.5, 13.5]
    Keys = ['{}:{}'.format(str(t), str(thres)) for t in G_Construct_Types for thres in CutOffThresholds]
    Results_error = dict()
    Results_Maj_error = dict()
    SelectedSerials = np.loadtxt(open(Path2SelectedSerial, 'rb'))
    #SelectedSerials = np.array(SelectedSerials[1:2])
    L = SelectedSerials.shape[0]

    for t in G_Construct_Types:
        for thres in CutOffThresholds:
            Results_error.update([('{}:{}'.format(str(t), str(thres)), [-1]*L)])
            Results_Maj_error.update([('{}:{}'.format(str(t), str(thres)), [-1]*L)])

    for idx, serial in enumerate(SelectedSerials):
        #Path2DynDomEntry = os.path.join(Dir2DynDomEntry, '{}.pkl'.format(str(serial)))
        #DD_Entry = pickle.load(open(Path2DynDomEntry, 'rb'))
        Path2Obj2Entry = os.path.join(Dir2SelectedEntryFinal, '{}.pkl'.format(str(serial)))
        Obj2_Entry = pickle.load(open(Path2Obj2Entry, 'rb'))
        serial = Obj2_Entry.Serial_Number
        Membership = Obj2_Entry.Membership
        for obj1 in Obj2_Entry.Array_Object_1:
            G_type = obj1.Graph_Construction_Type
            CutOff = obj1.Cut_Off_Threshold
            Partition_Labels = obj1.Labels
            #Partition_Labels = random_Labels(len(Membership), 20, 1234)
            error = eval_error(Membership, Partition_Labels)
            major_error = eval_majority_error(Membership, Partition_Labels)
            key = '{}:{}'.format(str(G_type), str(CutOff))
            Results_error[key][idx] = error
            Results_Maj_error[key][idx] = major_error

    '''write dictionary down to json files'''
    js1 = json.dumps(Results_error)
    js2 = json.dumps(Results_Maj_error)
    f1 = open('../MyDataSet/DynDom/Result_Error.json', 'wb')
    f2 = open('../MyDataSet/DynDom/Result_Majority_Error.json', 'wb')
    f1.write(js1); f1.close()
    f2.write(js2); f2.close()

    for k in Keys:
        #plt.hist(Results_error[k])
        print '{} \terror : {}'.format(k, ','.join(str(val) for val in Results_error[k]))
        print '{} \tmaj_error : {}'.format(k, ','.join(str(val) for val in Results_Maj_error[k]))




