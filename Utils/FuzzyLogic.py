import numpy as np
import skfuzzy as fuzz
import matplotlib
from skfuzzy import control as ctrl
#---------------------------------------




feature_node_low = [0, 0, 0.5]
feature_node_medium = [0.25, 0.5, 0.75]
feature_node_high = [0.5, 1, 1]

y_1 = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'y_1')
y_1['negative'] = fuzz.trapmf(y_1.universe, [-1, -1, 0, 0])
y_1['positive'] = fuzz.trapmf(y_1.universe, [0, 0, 1, 1])
# -------------------------------------------
y_2 = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'y_2')
y_2['negative'] = fuzz.trapmf(y_2.universe, [-1, -1, 0, 0])
y_2['positive'] = fuzz.trapmf(y_2.universe, [0, 0, 1, 1])
#-------------------------------------------------
y = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'y_i')
y['negative'] = fuzz.trapmf(y.universe, [-1, -1, 0, 0])
y['positive'] = fuzz.trapmf(y.universe, [0, 0, 1, 1])
#---------------------------------------
def init_output_fuzzyVar(output_range=[-1,1], output_negative=[-1, -1, 0], output_zero=[-0.3, 0, 0.3], output_positive=[0, 1, 1]):
    output = ctrl.Consequent(np.arange(output_range[0], output_range[1], 0.001), 'output')
    output['negative'] = fuzz.trimf(output.universe, output_negative)
    output['zero'] = fuzz.trimf(output.universe, output_zero)
    output['positive'] = fuzz.trimf(output.universe, output_positive)
    return output
#------------------------------------------------
def init_featureMid_fuzzyVar(fea_range=[0,1], feature_mid_small = [0, 0, 0.1, 0.4], feature_mid_medium = [0.25, 0.4, 0.55],
                             feature_mid_big=[0.5, 0.75, 1, 1]):
    feature_mid = ctrl.Antecedent(np.arange(fea_range[0], fea_range[1], 0.001), 'feature_mid')
    feature_mid['small'] = fuzz.trapmf(feature_mid.universe, feature_mid_small) if len(feature_mid_small)== 4 \
        else fuzz.trimf(feature_mid.universe, feature_mid_small)
    feature_mid['medium'] = fuzz.trimf(feature_mid.universe, feature_mid_medium) if len(feature_mid_medium)==3 \
        else fuzz.trapmf(feature_mid.universe, feature_mid_medium)
    feature_mid['big'] = fuzz.trapmf(feature_mid.universe, feature_mid_big) if len(feature_mid_big) == 4 \
        else fuzz.trimf(feature_mid.universe, feature_mid_big)
    return feature_mid
# -------------------------------------------
#-------------------------------------------------------


def estimateFuzzyFeature_Node(MeanVar, label1):
    output = init_output_fuzzyVar()
    feature = ctrl.Antecedent(np.arange(0, 1, 0.001), 'feature')
    feature['low'] = fuzz.trimf(feature.universe, feature_node_low) if len(feature_node_low) == 3 \
        else fuzz.trapmf(feature.universe, feature_node_low)
    feature['medium'] = fuzz.trimf(feature.universe, feature_node_medium) if len(feature_node_medium) == 3 \
        else fuzz.trapmf(feature.universe, feature_node_medium)
    feature['high'] = fuzz.trimf(feature.universe, feature_node_high) if len(feature_node_high) == 3 \
        else fuzz.trimf(feature.universe, feature_node_high)
    #----------------------------------------------------------------
    y_i = ctrl.Antecedent(np.arange(-1, 1, 0.01), 'y_i')
    y_i['negative'] = fuzz.trapmf(y_i.universe, [-1, -1, 0, 0])
    y_i['positive'] = fuzz.trapmf(y_i.universe, [0, 0, 1, 1])
    # --------------------------------------------
    rule1 = ctrl.Rule(y_i['negative'] & feature['low'], output['negative'])
    rule2 = ctrl.Rule(y_i['negative'] & feature['medium'], output['zero'])
    rule3 = ctrl.Rule(y_i['negative'] & feature['high'], output['positive'])
    rule4 = ctrl.Rule(y_i['positive'] & feature['low'], output['positive'])
    rule5 = ctrl.Rule(y_i['positive'] & feature['medium'], output['zero'])
    rule6 = ctrl.Rule(y_i['positive'] & feature['high'], output['negative'])
    rule = [rule1, rule2, rule3, rule4, rule5, rule6]
    #----------------------------------------------------------
    fea_ctrl = ctrl.ControlSystem(rule)
    fea_action = ctrl.ControlSystemSimulation(fea_ctrl)
    fea_action.input['feature'] = MeanVar
    fea_action.input['y_i'] = label1
    fea_action.compute()
    return fea_action.output['output']

def estimateFuzzyFeature_Edge2(MeanVar_mid, diff, label1, label2):
    feature_mid = init_featureMid_fuzzyVar()
    output = init_output_fuzzyVar()
    fea_diff = ctrl.Antecedent(np.arange(-2, 2, 0.01), 'feature_diff')
    fea_diff['negative'] = fuzz.trapmf(fea_diff.universe, [-2, -2, -1, -0.25])
    fea_diff['zero'] = fuzz.trimf(fea_diff.universe, [-0.5, 0, 0.5])
    fea_diff['positive'] = fuzz.trapmf(fea_diff.universe, [0.25, 1,2,2])
    #-------------------
    rule1 = ctrl.Rule(y_1['positive'] & y_2['positive'] & (feature_mid['small'] | feature_mid['medium']), output['positive'])
    rule2 = ctrl.Rule(y_1['positive'] & y_2['positive'] & feature_mid['big'], output['negative'])
    rule3 = ctrl.Rule(y_1['negative'] & y_2['negative'] & feature_mid['small'] & (fea_diff['negative'] | fea_diff['zero']), output['positive'])
    rule4 = ctrl.Rule(y_1['negative'] & y_2['negative'] & feature_mid['small'] & fea_diff['positive'], output['zero'])
    rule5 = ctrl.Rule(((y_1['positive'] & y_2['negative']) | (y_1['negative'] & y_2['positive'])) & feature_mid['small'] &
                      (fea_diff['negative'] | fea_diff['zero']), output['negative'])
    rule6 = ctrl.Rule(((y_1['positive'] & y_2['negative']) | (y_1['negative'] & y_2['positive'])) & feature_mid['small'] &
                      fea_diff['positive'], output['zero'])
    rule7 = ctrl.Rule(y_1['negative'] & y_2['negative'] & feature_mid['medium'] & (fea_diff['negative'] | fea_diff['positive']),
                      output['zero'])
    rule8 = ctrl.Rule(y_1['negative'] & y_2['negative'] & feature_mid['medium'] & fea_diff['zero'], output['negative'])
    rule9 = ctrl.Rule(y_1['negative'] & y_2['positive'] & feature_mid['medium'] & (fea_diff['negative'] | fea_diff['zero']), output['zero'])
    rule10 = ctrl.Rule(y_1['negative'] & y_2['positive'] & feature_mid['medium'] & fea_diff['positive'], output['positive'])
    rule11 = ctrl.Rule(y_1['positive'] & y_2['negative'] & feature_mid['medium'] & fea_diff['negative'], output['positive'])
    rule12 = ctrl.Rule(y_1['positive'] & y_2['negative'] & feature_mid['medium'] & (fea_diff['zero'] | fea_diff['positive']),output['zero'])
    rule13 = ctrl.Rule(y_1['negative'] & feature_mid['big'] & fea_diff['negative'], output['negative'])
    rule14 = ctrl.Rule(y_1['negative'] & feature_mid['big'] & fea_diff['zero'], output['positive'])
    rule15 = ctrl.Rule(y_1['positive'] & y_2['negative'] & feature_mid['big'] & (fea_diff['negative'] | fea_diff['zero']), output['positive'])
    rule16 = ctrl.Rule(y_2['negative'] & feature_mid['big'] & fea_diff['positive'], output['negative'])
    rule17 = ctrl.Rule(y_1['negative'] & y_2['positive'] & feature_mid['big'] & fea_diff['positive'], output['positive'])
    rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17]

    fea_ctrl = ctrl.ControlSystem(rules)
    fea_action = ctrl.ControlSystemSimulation(fea_ctrl)
    fea_action.input['feature_mid'] = MeanVar_mid
    fea_action.input['feature_diff'] = diff
    fea_action.input['y_1'] = label1
    fea_action.input['y_2'] = label2
    fea_action.compute()
    return fea_action.output['output']

def estimateFuzzyFeature_Edge(MeanVar_mid, label1, label2):
    #def estimateFuzzyFeature_Edge(MeanVar_mid, MeanVar_1, MeanVar_2, label1, label2):
    '''feature_mid = ctrl.Antecedent(np.arange(0, 1, 0.001), 'feature_mid')
    feature_mid['low'] = fuzz.trimf(feature_mid.universe, [0, 0, 0.5])
    feature_mid['medium'] = fuzz.trimf(feature_mid.universe, [0.25, 0.5, 0.75])
    feature_mid['high'] = fuzz.trimf(feature_mid.universe, [0.5, 1, 1])'''
    #-------------------------------------------
    feature_mid = init_featureMid_fuzzyVar()
    output = init_output_fuzzyVar()
    feature_1 = ctrl.Antecedent(np.arange(0, 1, 0.001), 'feature_1')
    feature_1['low'] = fuzz.trimf(feature_1.universe, [0, 0, 0.5])
    feature_1['medium'] = fuzz.trimf(feature_1.universe, [0.25, 0.5, 0.75])
    feature_1['high'] = fuzz.trimf(feature_1.universe, [0.5, 1, 1])
    #----------------------------------------------
    feature_2 = ctrl.Antecedent(np.arange(0, 1, 0.001), 'feature_2')
    feature_2['low'] = fuzz.trimf(feature_2.universe, [0, 0, 0.5])
    feature_2['medium'] = fuzz.trimf(feature_2.universe, [0.25, 0.5, 0.75])
    feature_2['high'] = fuzz.trimf(feature_2.universe, [0.5, 1, 1])
    #-------------------------------------------
    y_i = ctrl.Antecedent(np.arange(-1,1, 0.01), 'y_i')
    y_i['negative'] = fuzz.trapmf(y_i.universe, [-1, -1, 0, 0])
    y_i['positive'] = fuzz.trapmf(y_i.universe, [0, 0, 1, 1])
    #-------------------------------------------
    y_j = ctrl.Antecedent(np.arange(-1,1, 0.01), 'y_j')
    y_j['negative'] = fuzz.trapmf(y_j.universe, [-1, -1, 0, 0])
    y_j['positive'] = fuzz.trapmf(y_j.universe, [0, 0, 1, 1])
    #--------------------------------------------
    '''output = ctrl.Consequent(np.arange(-2,2,0.005), 'output')
    output['negative'] = fuzz.trimf(output.universe, [-2, -1, 0])
    output['zero'] = fuzz.trimf(output.universe, [-1, 0, 1])
    output['positive'] = fuzz.trimf(output.universe, [0, 1, 2]) '''
    #--------------------------------------------
    rule = []
    rule1 = ctrl.Rule(y_i['negative'] & y_j['negative'] & feature_mid['low'], output['zero']); rule.append(rule1)
    rule2 = ctrl.Rule(y_i['negative'] & y_j['negative'] & feature_mid['medium'], output['negative']); rule.append(rule2)
    rule3 = ctrl.Rule(y_i['negative'] & y_j['negative'] & feature_mid['high'], output['positive']); rule.append(rule3)
    rule4 = ctrl.Rule(y_i['negative'] & y_j['positive'] & feature_mid['low'], output['negative']); rule.append(rule4)
    rule5 = ctrl.Rule(y_i['negative'] & y_j['positive'] & feature_mid['medium'], output['zero']); rule.append(rule5)
    rule6 = ctrl.Rule(y_i['negative'] & y_j['positive'] & feature_mid['high'], output['positive']); rule.append(rule6)
    rule7 = ctrl.Rule(y_i['positive'] & y_j['negative'] & feature_mid['low'], output['negative']); rule.append(rule7)
    rule8 = ctrl.Rule(y_i['positive'] & y_j['negative'] & feature_mid['medium'], output['zero']); rule.append(rule8)
    rule9 = ctrl.Rule(y_i['positive'] & y_j['negative'] & feature_mid['high'], output['positive']); rule.append(rule9)
    rule10 = ctrl.Rule(y_i['positive'] & y_j['positive'] & feature_mid['low'], output['positive']); rule.append(rule10)
    rule11 = ctrl.Rule(y_i['positive'] & y_j['positive'] & feature_mid['medium'], output['positive']); rule.append(rule11)
    rule12 = ctrl.Rule(y_i['positive'] & y_j['positive'] & feature_mid['high'], output['negative']); rule.append(rule12)

    fea_ctrl = ctrl.ControlSystem(rule)
    fea_action = ctrl.ControlSystemSimulation(fea_ctrl)
    fea_action.input['feature_mid'] = MeanVar_mid
    fea_action.input['y_i'] = label1
    fea_action.input['y_j'] = label2
    fea_action.compute()
    return fea_action.output['output']

    #-------------------------------------------

def estimateFF_Vertex_Sim(Val, label, RangeOfSmall, RangeOfBig, fea_range=[0,1]):
    FV_feature = ctrl.Antecedent(np.arange(fea_range[0], fea_range[1], 0.001), 'FV_feature')
    FV_feature['small'] = fuzz.trimf(FV_feature.universe, RangeOfSmall) if len(RangeOfSmall) == 3 \
        else fuzz.trapmf(FV_feature.universe, RangeOfSmall)
    FV_feature['big'] = fuzz.trimf(FV_feature.universe, RangeOfBig) if len(RangeOfBig) == 3 \
        else fuzz.trapmf(FV_feature.universe, RangeOfBig)
    output = init_output_fuzzyVar()



if __name__=="__main__":
    print estimateFuzzyFeature_Edge(0.78, 1, 1)

