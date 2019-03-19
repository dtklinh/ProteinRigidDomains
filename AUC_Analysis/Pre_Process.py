

def draw_GraphConstructionType_Threshold():
    import json
    import matplotlib.pyplot as plt
    import numpy as np

    data = []
    with open('./MyDataSet/DynDom/Result_Error.json') as f:
        data = json.load(f)
    data2 = []
    with open('./MyDataSet/DynDom/Result_Majority_Error.json') as f:
        data2 = json.load(f)
    data_rnd = []
    with open('./MyDataSet/DynDom/Result_Error_Rnd.json') as f:
        data_rnd = json.load(f)
    data2_rnd = []
    with open('./MyDataSet/DynDom/Result_Majority_Error_Rnd.json') as f:
        data2_rnd = json.load(f)

    fig, ax = plt.subplots(3, 3, sharex=True, sharey=True, figsize=(16, 8))
    cutoff = [7.5, 10.5, 13.5]
    D1 = data
    D2 = data_rnd
    for i, thres in enumerate(cutoff):
        k = '0:{}'.format(str(thres))
        x_label = 'Error'
        ax[i][0].hist(D1[k], bins=np.arange(0, 0.20, 0.002))
        ax[i][0].set_title('Louvain Algorithm')
        ax[i][0].set_ylabel('CutOff={}'.format(str(thres)))
        ax[i][0].set_xlabel(x_label)
        ax[i][1].hist(D2[k], bins=np.arange(0, 0.22, 0.002), color='red')
        ax[i][1].set_title('Equal 20 chunks')
        ax[i][1].set_xlabel(x_label)
        ax[i][2].hist(D1[k], bins=np.arange(0, 0.22, 0.002), alpha=0.55, color='blue')
        ax[i][2].hist(D2[k], bins=np.arange(0, 0.22, 0.002), alpha=0.55, color='red')
        ax[i][2].set_title('Both')
        ax[i][2].set_xlabel(x_label)

    fig.text(-0.01, 0.5, 'common Y', va='center', rotation='vertical')
    fig.tight_layout()
    plt.show()
    fig.savefig('./MyDataSet/DynDom/Fig_ConstructType_0_OverlapError_489_tmp.png')


if __name__=='__main__':
