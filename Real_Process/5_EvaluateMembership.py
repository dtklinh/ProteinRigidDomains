from PathAndDir import Dir2Membership, Path2SelectedSerial
from MyIO import ReadLines
from Evaluation_funcs import overlap, error_MemMershipMatrix
import os, concurrent.futures, time
import numpy as np

def do_work(serial):
    Lines = ReadLines(os.path.join(Dir2Membership, '{}.txt'.format(str(serial))))
    Membership = [int(i) for i in Lines[0].split()]
    BestPossibleLabel = [int(i) for i in Lines[1].split()]
    PredLabel = [int(i) for i in Lines[2].split()]
    BestPossible_Error = error_MemMershipMatrix(Membership, BestPossibleLabel)
    BestPossible_Overlap = overlap(Membership, BestPossibleLabel)

    Pred_Error = error_MemMershipMatrix(Membership, PredLabel)
    Pred_Overlap = overlap(Membership, PredLabel)

    return serial, BestPossible_Error, BestPossible_Overlap, Pred_Error, Pred_Overlap

if __name__=='__main__':
    t_start = time.time()
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #serial = 559

    Arr_Best_Error = []
    Arr_Best_Overlap = []
    Arr_Pred_Error = []
    Arr_Pred_Overlap = []

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

            Arr_Best_Error.append(val[1])
            Arr_Best_Overlap.append(val[2])
            Arr_Pred_Error.append(val[3])
            Arr_Pred_Overlap.append(val[4])

            print 'Finish: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()


    print "AVERAGE Best ERROR: {}".format(str(np.mean(Arr_Best_Error)))
    print "AVERAGE Best OVERLAP: {}".format(str(np.mean(Arr_Best_Overlap)))
    print "MEDIAN Best ERROR: {}".format(str(np.median(Arr_Best_Error)))
    print "MEDIAN Best OVERLAP: {}".format(str(np.median(Arr_Best_Overlap)))
    print '------------------------'
    print "AVERAGE Pred ERROR: {}".format(str(np.mean(Arr_Pred_Error)))
    print "AVERAGE Pred OVERLAP: {}".format(str(np.mean(Arr_Pred_Overlap)))
    print "MEDIAN Pred ERROR: {}".format(str(np.median(Arr_Pred_Error)))
    print "MEDIAN Pred OVERLAP: {}".format(str(np.median(Arr_Pred_Overlap)))
