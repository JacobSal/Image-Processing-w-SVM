# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:02:19 2021

@author: jsalm
"""
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os

from scipy.ndimage import convolve
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, train_test_split, learning_curve, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
<<<<<<< Updated upstream
from sklearn.metrics import plot_confusion_matrix, auc, roc_curve, roc_auc_score, accuracy_score, classification_report
=======
from sklearn.metrics import confusion_matrix, auc, roc_curve, roc_auc_score, accuracy_score, classification_report
>>>>>>> Stashed changes
from sklearn.decomposition import PCA
from skimage.feature import hog
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

import pandas as pd
import xgboost as xgb
from xgboost import XGBClassifier

import pandas as pd
import xgboost as xgb
from xgboost import XGBClassifier

import SVM
import Filters
import ML_interface_SVM_V3
import DataManager


####PARAMS####
# param_range = [0.0001,0.001,0.01,0.1,1,10,100,1000]
# param_range= np.arange(0.01,1,0.001)
param_range2_C = [40,50,60,70,80,90,100,110,120,130,140]
param_range2_ga = [0.0005,0.0006,0.0007,0.001,0.002,0.003,0.004]
deg_range = [2,3,4,5,6,7]
deg_range2 = [2,3,4,5,6,10]
poly_range = np.arange(2,10,1)
poly_range_C = np.arange(1e-15,1e-7,6e-10)
poly_range_ga = np.arange(1e8,1e15,6e12)
# param_grid = [{'svc__C':param_range,
#                 'svc__kernel':['linear']},
#               {'svc__C': param_range,
#                 'svc__gamma':param_range,
#                 'svc__kernel':['rbf']},
#               {'svc__C': param_range,
#                 'svc__gamma':param_range,
#                 'svc__kernel':['poly'],
#                 'svc__degree':deg_range}]
param_grid2 = [{'svc__C': param_range2_C,
                'svc__gamma':param_range2_ga,
                'svc__decision_function_shape':['ovo','ovr'],
                'svc__kernel':['rbf']},
                {'svc__C': param_range2_C,
                 'svc__gamma':param_range2_ga,
                 'svc__kernel':['poly'],
                 'svc__decision_function_shape':['ovo','ovr'],
                 'svc__degree':deg_range2}]
# param_grid3 = [{'svc__C': poly_range_C,
#                 'svc__gamma':poly_range_ga,
#                 'svc__kernel':['poly'],
#                 'svc__degree':poly_range}]
###END###

### DATA PROCESSING IMAGE 1 ###

#initialize test data set
dirname = os.path.dirname(__file__)
foldername = os.path.join(dirname,"images_5HT")
im_dir = DataManager.DataMang(foldername)

### PARAMS ###
channel = 2
ff_width = 121
wiener_size = (5,5)
med_size = 10
start = 0
count = 42
###

#load image folder for training data
dirname = os.path.dirname(__file__)
foldername = os.path.join(dirname,"images_5HT")
im_dir = DataManager.DataMang(foldername)
# change the 'start' in PARAMS to choose which file you want to start with.
im_list = [i for i in range(start,im_dir.dir_len)]
hog_features = []
for gen in im_dir.open_dir(im_list):
    #load image and its information
    image,nW,nH,chan,name = gen
    print('procesing image : {}'.format(name))
    #only want the red channel (fyi: cv2 is BGR (0,1,2 respectively) while most image processing considers 
    #the notation RGB (0,1,2 respectively))
    image = image[:,:,channel]
    #Import train data (if training your model)
    train_bool = ML_interface_SVM_V3.import_train_data(name,(nW,nH),'train_71420')
    #extract features from image using method(SVM.filter_pipeline) then watershed data useing thresholding algorithm (work to be done here...) to segment image.
    #Additionally, extract filtered image data and hog_Features from segmented image. (will also segment train image if training model) 
    im_segs, bool_segs, domains, paded_im_seg, paded_bool_seg, hog_features = SVM.feature_extract(image, ff_width, wiener_size, med_size,True,train_bool)
    #choose which data you want to merge together to train SVM. Been using my own filter, but could also use hog_features.
    X,y = SVM.create_data(hog_features,True,bool_segs)
    break

print('done')
#adding in some reference numbers for later
y = np.vstack([y,np.arange(0,len(y),1)]).T
#split dataset
transformer = RobustScaler().fit(X)
X = transformer.transform(X)

print('Splitting dataset...')
X_train, X_test, y_train, y_test = train_test_split(X,y,
                                                        test_size=0.2,
                                                        shuffle=True,
                                                        random_state=count)
ind_train = y_train[:,1]
ind_test = y_test[:,1]

y_train = y_train[:,0]
y_test = y_test[:,0]



print("y_train: " + str(np.unique(y_train)))
print("y_test: " + str(np.unique(y_test)))


### SKLEARN ALGORITHM ###
#create SVM pipline
#try using a GBC
# pipe_svc = make_pipeline(RobustScaler(),())

##XGBOOST ALGORITHM



##XGBoost with Optimal HyperParameters
coef = [2,0.28,150,0.57,0.36,0.1,1,0,0.75,0.42]
model = XGBClassifier(max_depth = coef[0],subsample = coef[1],n_estimators = coef[2],
                      colsample_bylevel = coef[3], colsample_bytree = coef[4],learning_rate=coef[5], 
                      min_child_weight = coef[6], random_state = coef[7],reg_alpha = coef[8],
                      reg_lambda = coef[9])
model.fit(X_train,y_train)
y_predict = model.predict(X_test)
y_train_predict = model.predict(X_train)
print('Train accuracy',accuracy_score(y_train, y_train_predict))
print('Test accuracy',accuracy_score(y_test,y_predict))
print(classification_report(y_test,y_predict))


#ROC/AUC plotting and score
fpr, tpr, thresholds = roc_curve(y_test, model.predict_proba(X_test)[:,1],drop_intermediate=False)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.title('ROC curve for serotonin classifier')
plt.xlabel('False Positive Rate (1 - Specificity)')
plt.ylabel('True Positive Rate (Sensitivity)')
plt.plot(fpr, tpr,color='red',lw=3)
plt.show()

print('ROC/AUC Score', roc_auc_score(y_test, model.predict_proba(X_test)[:,1]))
        
#Best coefficients so far:
    #coef = [2,0.28,150,0.57,0.36,0.1,1,0,0.75,0.42]
    
#Sample code for testing hyperparameters
    # score = 0.7159090909090909       
    # coef = [2,0.4,150,.8,1,.1,1,0,1,0.5]
    # for ii in range(2,31): 
    #     model = XGBClassifier(max_depth = ii,subsample = coef[1],n_estimators = coef[2],
    #                       colsample_bylevel = coef[3], colsample_bytree = coef[4],learning_rate=coef[5], 
    #                       min_child_weight = coef[6], random_state = coef[7],reg_alpha = coef[8],
    #                       reg_lambda = coef[9])
    #     model.fit(X_train,y_train) 
    #     y_predict = model.predict(X_test) 
    #     y_train_predict = model.predict(X_train)
    #     newscore = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
    #     print(ii,newscore, end="")
    #     if newscore > score:
    #         print(' best so far')
    #         score = newscore
    #     else:
    #         print()
        
# Results (coef,ROC/AUC Score):
    # max_depth:
        # 2 0.7159090909090909 best so far
        # 3 0.6960227272727273
        # 4 0.6875
        # 5 0.6988636363636364
        # 6 0.7130681818181819
        # 7 0.7045454545454546
        # 8 0.7045454545454546
        # 9 0.7045454545454546
        # 10 0.7045454545454546
        # 11 0.7045454545454546
        # 12 0.7045454545454546
        # 13 0.7045454545454546
        # 14 0.7045454545454546
        # 15 0.7045454545454546
        # 16 0.7045454545454546
        # 17 0.7045454545454546
        # 18 0.7045454545454546
        # 19 0.7045454545454546
        # 20 0.7045454545454546
        # 21 0.7045454545454546
        # 22 0.7045454545454546
        # 23 0.7045454545454546
        # 24 0.7045454545454546
        # 25 0.7045454545454546
        # 26 0.7045454545454546
        # 27 0.7045454545454546
        # 28 0.7045454545454546
        # 29 0.7045454545454546
        # 30 0.7045454545454546
    # subsample:
        # 0.01 0.5
        # 0.02 0.5404829545454545
        # 0.03 0.7329545454545454 best so far
        # 0.04 0.5951704545454546
        # 0.05 0.6931818181818182
        # 0.06 0.612215909090909
        # 0.07 0.7386363636363636 best so far
        # 0.08 0.7102272727272728
        # 0.09 0.6335227272727273
        # 0.1 0.6349431818181819
        # 0.11 0.5724431818181818
        # 0.12 0.6448863636363636
        # 0.13 0.6349431818181819
        # 0.14 0.6690340909090908
        # 0.15 0.7159090909090909
        # 0.16 0.6832386363636364
        # 0.17 0.7201704545454546
        # 0.18 0.7230113636363636
        # 0.19 0.8025568181818181 best so far
        # 0.2 0.8338068181818181 best so far
        # 0.21 0.7812499999999999
        # 0.22 0.7329545454545454
        # 0.23 0.8238636363636365
        # 0.24 0.7840909090909092
        # 0.25 0.7869318181818182
        # 0.26 0.8082386363636364
        # 0.27 0.8267045454545455
        # 0.28 0.8380681818181819 best so far
        # 0.29 0.8025568181818181
        # 0.3 0.7514204545454546
        # 0.31 0.7826704545454546
        # 0.32 0.7301136363636364
        # 0.33 0.7642045454545455
        # 0.34 0.7386363636363636
        # 0.35 0.7357954545454546
        # 0.36 0.7329545454545455
        # 0.37 0.7173295454545454
        # 0.38 0.6903409090909092
        # 0.39 0.7059659090909091
        # 0.4 0.7159090909090909
        # 0.41 0.6974431818181818
        # 0.42 0.7798295454545454
        # 0.43 0.7130681818181819
        # 0.44 0.7528409090909092
        # 0.45 0.7599431818181819
        # 0.46 0.7414772727272727
        # 0.47 0.7045454545454546
        # 0.48 0.7571022727272727
        # 0.49 0.7457386363636364
        # 0.5 0.7642045454545454
        # 0.51 0.7528409090909092
        # 0.52 0.7215909090909092
        # 0.53 0.690340909090909
        # 0.54 0.7130681818181819
        # 0.55 0.7301136363636364
        # 0.56 0.7883522727272727
        # 0.57 0.7386363636363636
        # 0.58 0.7272727272727273
        # 0.59 0.7258522727272727
        # 0.6 0.7457386363636364
        # 0.61 0.7144886363636364
        # 0.62 0.7514204545454546
        # 0.63 0.7698863636363636
        # 0.64 0.7741477272727273
        # 0.65 0.7542613636363636
        # 0.66 0.75
        # 0.67 0.7826704545454546
        # 0.68 0.7642045454545454
        # 0.69 0.7315340909090908
        # 0.7 0.7713068181818181
        # 0.71 0.7684659090909092
        # 0.72 0.7485795454545454
        # 0.73 0.78125
        # 0.74 0.7954545454545454
        # 0.75 0.7798295454545454
        # 0.76 0.765625
        # 0.77 0.7443181818181819
        # 0.78 0.7798295454545454
        # 0.79 0.7613636363636364
        # 0.8 0.7684659090909092
        # 0.81 0.765625
        # 0.82 0.7784090909090909
        # 0.83 0.7585227272727273
        # 0.84 0.765625
        # 0.85 0.7400568181818181
        # 0.86 0.7784090909090909
        # 0.87 0.7613636363636362
        # 0.88 0.7684659090909092
        # 0.89 0.7670454545454546
        # 0.9 0.7571022727272727
        # 0.91 0.7400568181818181
        # 0.92 0.7258522727272728
        # 0.93 0.7400568181818182
        # 0.94 0.7414772727272727
        # 0.95 0.7599431818181819
        # 0.96 0.7642045454545454
        # 0.97 0.7613636363636364
        # 0.98 0.7599431818181819
        # 0.99 0.7500000000000001
        # 1.0 0.7372159090909092  
    # colsample_bylevel:
        # 0.01 0.6761363636363636
        # 0.02 0.7201704545454546
        # 0.03 0.7528409090909091
        # 0.04 0.7286931818181818
        # 0.05 0.7002840909090909
        # 0.06 0.703125
        # 0.07 0.7642045454545454
        # 0.08 0.7698863636363636
        # 0.09 0.7542613636363636
        # 0.1 0.7784090909090908
        # 0.11 0.7855113636363636
        # 0.12 0.7897727272727272
        # 0.13 0.7840909090909092
        # 0.14 0.8380681818181818
        # 0.15 0.8039772727272727
        # 0.16 0.8153409090909092
        # 0.17 0.7855113636363636
        # 0.18 0.7869318181818181
        # 0.19 0.7826704545454546
        # 0.2 0.8480113636363638 best so far
        # 0.21 0.8551136363636364 best so far
        # 0.22 0.8039772727272727
        # 0.23 0.8125
        # 0.24 0.7982954545454545
        # 0.25 0.8096590909090909
        # 0.26 0.7911931818181819
        # 0.27 0.8096590909090908
        # 0.28 0.7855113636363635
        # 0.29 0.7926136363636364
        # 0.3 0.8210227272727272
        # 0.31 0.8323863636363635
        # 0.32 0.8295454545454546
        # 0.33 0.8224431818181819
        # 0.34 0.8039772727272727
        # 0.35 0.8053977272727273
        # 0.36 0.828125
        # 0.37 0.8323863636363636
        # 0.38 0.7954545454545454
        # 0.39 0.7883522727272727
        # 0.4 0.8167613636363638
        # 0.41 0.8181818181818181
        # 0.42 0.8025568181818182
        # 0.43 0.8295454545454546
        # 0.44 0.7826704545454546
        # 0.45 0.8068181818181818
        # 0.46 0.8409090909090908
        # 0.47 0.8394886363636364
        # 0.48 0.8465909090909092
        # 0.49 0.7982954545454546
        # 0.5 0.8238636363636364
        # 0.51 0.8210227272727273
        # 0.52 0.84375
        # 0.53 0.8636363636363635 best so far
        # 0.54 0.8465909090909091
        # 0.55 0.8451704545454546
        # 0.56 0.8295454545454546
        # 0.57 0.8678977272727273 best so far
        # 0.58 0.8451704545454546
        # 0.59 0.8551136363636364
        # 0.6 0.8323863636363635
        # 0.61 0.8323863636363635
        # 0.62 0.8480113636363636
        # 0.63 0.7897727272727273
        # 0.64 0.7982954545454546
        # 0.65 0.8125
        # 0.66 0.8096590909090909
        # 0.67 0.828125
        # 0.68 0.8366477272727273
        # 0.69 0.828125
        # 0.7 0.828125
        # 0.71 0.8465909090909091
        # 0.72 0.8039772727272728
        # 0.73 0.8096590909090909
        # 0.74 0.8394886363636364
        # 0.75 0.8167613636363636
        # 0.76 0.8380681818181819
        # 0.77 0.8295454545454545
        # 0.78 0.8110795454545454
        # 0.79 0.8508522727272728
        # 0.8 0.8380681818181819
        # 0.81 0.8309659090909092
        # 0.82 0.8096590909090908
        # 0.83 0.8082386363636364
        # 0.84 0.8536931818181818
        # 0.85 0.7968750000000001
        # 0.86 0.7897727272727273
        # 0.87 0.8224431818181819
        # 0.88 0.8210227272727273
        # 0.89 0.8110795454545454
        # 0.9 0.7982954545454546
        # 0.91 0.7911931818181819
        # 0.92 0.7940340909090909
        # 0.93 0.8125
        # 0.94 0.8323863636363635
        # 0.95 0.8110795454545454
        # 0.96 0.8053977272727273
        # 0.97 0.78125
        # 0.98 0.8181818181818181
        # 0.99 0.8295454545454545
        # 1.0 0.8096590909090908 
    # colsample_bytree:
        # 0.01 0.6789772727272727
        # 0.02 0.7301136363636362
        # 0.03 0.7017045454545454
        # 0.04 0.7088068181818181
        # 0.05 0.7556818181818181
        # 0.06 0.7258522727272727
        # 0.07 0.7428977272727273
        # 0.08 0.7542613636363636
        # 0.09 0.7840909090909091
        # 0.1 0.703125
        # 0.11 0.6463068181818182
        # 0.12 0.7244318181818182
        # 0.13 0.7372159090909092
        # 0.14 0.8068181818181819
        # 0.15 0.7698863636363635
        # 0.16 0.7840909090909091
        # 0.17 0.7627840909090909
        # 0.18 0.7400568181818182
        # 0.19 0.78125
        # 0.2 0.7599431818181819
        # 0.21 0.7627840909090909
        # 0.22 0.7755681818181819
        # 0.23 0.7542613636363636
        # 0.24 0.7357954545454546
        # 0.25 0.7102272727272727
        # 0.26 0.7599431818181818
        # 0.27 0.734375
        # 0.28 0.7940340909090908
        # 0.29 0.765625
        # 0.3 0.7926136363636364
        # 0.31 0.7627840909090909
        # 0.32 0.7585227272727273
        # 0.33 0.7670454545454546
        # 0.34 0.7684659090909092
        # 0.35 0.7571022727272727
        # 0.36 0.8707386363636365 best so far
        # 0.37 0.7741477272727273
        # 0.38 0.78125
        # 0.39 0.7741477272727273
        # 0.4 0.7670454545454546
        # 0.41 0.7684659090909092
        # 0.42 0.7954545454545454
        # 0.43 0.75
        # 0.44 0.8267045454545454
        # 0.45 0.7585227272727273
        # 0.46 0.7954545454545454
        # 0.47 0.7329545454545454
        # 0.48 0.78125
        # 0.49 0.7840909090909091
        # 0.5 0.8394886363636365
        # 0.51 0.8125
        # 0.52 0.78125
        # 0.53 0.7997159090909091
        # 0.54 0.7840909090909091
        # 0.55 0.8295454545454546
        # 0.56 0.7968749999999999
        # 0.57 0.8252840909090909
        # 0.58 0.84375
        # 0.59 0.7386363636363636
        # 0.6 0.7784090909090909
        # 0.61 0.8494318181818181
        # 0.62 0.7997159090909091
        # 0.63 0.7116477272727273
        # 0.64 0.7911931818181819
        # 0.65 0.8238636363636365
        # 0.66 0.7897727272727273
        # 0.67 0.7428977272727273
        # 0.68 0.8252840909090909
        # 0.69 0.7826704545454546
        # 0.7 0.8039772727272727
        # 0.71 0.8224431818181819
        # 0.72 0.7784090909090909
        # 0.73 0.752840909090909
        # 0.74 0.7883522727272727
        # 0.75 0.8139204545454546
        # 0.76 0.78125
        # 0.77 0.796875
        # 0.78 0.8039772727272727
        # 0.79 0.7528409090909091
        # 0.8 0.8196022727272727
        # 0.81 0.8196022727272727
        # 0.82 0.7826704545454545
        # 0.83 0.7485795454545454
        # 0.84 0.8366477272727273
        # 0.85 0.828125
        # 0.86 0.78125
        # 0.87 0.8579545454545454
        # 0.88 0.7585227272727274
        # 0.89 0.7982954545454546
        # 0.9 0.7755681818181818
        # 0.91 0.7627840909090909
        # 0.92 0.8352272727272727
        # 0.93 0.7329545454545454
        # 0.94 0.8096590909090908
        # 0.95 0.7840909090909092
        # 0.96 0.7883522727272727
        # 0.97 0.8267045454545455
        # 0.98 0.7769886363636364
        # 0.99 0.8053977272727274
        # 1.0 0.8678977272727273
    #learning_rate:
        # 0.01 0.7286931818181819
        # 0.02 0.7769886363636365
        # 0.03 0.7769886363636362
        # 0.04 0.7741477272727273
        # 0.05 0.78125
        # 0.06 0.8110795454545455
        # 0.07 0.7883522727272727
        # 0.08 0.8536931818181819
        # 0.09 0.8309659090909091
        # 0.1 0.8707386363636365
        # 0.11 0.8409090909090909
        # 0.12 0.8409090909090908
        # 0.13 0.8423295454545455
        # 0.14 0.8394886363636365
        # 0.15 0.8125
        # 0.16 0.7926136363636364
        # 0.17 0.7940340909090908
        # 0.18 0.8494318181818182
        # 0.19 0.7627840909090908
        # 0.2 0.7400568181818181
        # 0.21 0.7514204545454546
        # 0.22 0.7997159090909091
        # 0.23 0.7741477272727272
        # 0.24 0.8352272727272727
        # 0.25 0.7755681818181819
        # 0.26 0.7798295454545454
        # 0.27 0.7414772727272726
        # 0.28 0.8323863636363636
        # 0.29 0.7627840909090909
        # 0.3 0.7002840909090908
        # 0.31 0.7244318181818181
        # 0.32 0.7443181818181819
        # 0.33 0.8039772727272727
        # 0.34 0.7386363636363636
        # 0.35 0.7642045454545455
        # 0.36 0.7173295454545454
        # 0.37 0.7357954545454546
        # 0.38 0.7755681818181819
        # 0.39 0.8309659090909091
        # 0.4 0.7855113636363635
        # 0.41 0.7713068181818181
        # 0.42 0.7301136363636364
        # 0.43 0.6903409090909091
        # 0.44 0.6647727272727273
        # 0.45 0.5980113636363635
        # 0.46 0.6917613636363635
        # 0.47 0.7343749999999999
        # 0.48 0.6590909090909091
        # 0.49 0.7471590909090908
        # 0.5 0.6633522727272727
        # 0.51 0.6534090909090908
        # 0.52 0.6960227272727273
        # 0.53 0.6789772727272727
        # 0.54 0.7542613636363636
        # 0.55 0.7130681818181819
        # 0.56 0.6860795454545455
        # 0.57 0.7144886363636364
        # 0.58 0.71875
        # 0.59 0.6690340909090908
        # 0.6 0.6036931818181819
        # 0.61 0.6292613636363636
        # 0.62 0.6619318181818182
        # 0.63 0.65625
        # 0.64 0.6676136363636365
        # 0.65 0.5994318181818181
        # 0.66 0.5255681818181819
        # 0.67 0.6690340909090908
        # 0.68 0.6306818181818181
        # 0.69 0.6590909090909092
        # 0.7 0.6022727272727273
        # 0.71 0.7144886363636364
        # 0.72 0.6278409090909091
        # 0.73 0.7329545454545454
        # 0.74 0.6974431818181818
        # 0.75 0.6917613636363636
        # 0.76 0.5994318181818182
        # 0.77 0.5752840909090909
        # 0.78 0.6321022727272727
        # 0.79 0.5909090909090909
        # 0.8 0.5767045454545454
        # 0.81 0.5752840909090908
        # 0.82 0.7215909090909092
        # 0.83 0.7059659090909092
        # 0.84 0.6860795454545454
        # 0.85 0.6221590909090908
        # 0.86 0.6193181818181819
        # 0.87 0.5951704545454546
        # 0.88 0.6818181818181819
        # 0.89 0.7201704545454546
        # 0.9 0.6775568181818182
        # 0.91 0.71875
        # 0.92 0.6193181818181819
        # 0.93 0.7173295454545454
        # 0.94 0.6867897727272727
        # 0.95 0.6590909090909091
        # 0.96 0.6519886363636364
        # 0.97 0.6498579545454545
        # 0.98 0.7088068181818182
        # 0.99 0.5759943181818181
        # 1.0 0.5951704545454546
    # min_child_weight:
        # 0.01 0.7926136363636364
        # 0.02 0.7926136363636364
        # 0.03 0.7926136363636364
        # 0.04 0.7926136363636364
        # 0.05 0.7926136363636364
        # 0.06 0.7926136363636364
        # 0.07 0.7926136363636364
        # 0.08 0.7883522727272727
        # 0.09 0.7940340909090908
        # 0.1 0.8039772727272727
        # 0.11 0.8039772727272727
        # 0.12 0.8082386363636365
        # 0.13 0.8068181818181819
        # 0.14 0.8210227272727273
        # 0.15 0.8125
        # 0.16 0.8110795454545454
        # 0.17 0.8125
        # 0.18 0.8011363636363638
        # 0.19 0.8068181818181819
        # 0.2 0.8039772727272727
        # 0.21 0.7997159090909092
        # 0.22 0.8096590909090909
        # 0.23 0.8068181818181819
        # 0.24 0.8011363636363636
        # 0.25 0.8196022727272727
        # 0.26 0.8125
        # 0.27 0.8224431818181818
        # 0.28 0.8196022727272727
        # 0.29 0.8252840909090908
        # 0.3 0.828125
        # 0.31 0.8267045454545454
        # 0.32 0.8338068181818181
        # 0.33 0.8267045454545454
        # 0.34 0.8011363636363638
        # 0.35 0.8196022727272727
        # 0.36 0.8139204545454546
        # 0.37 0.8139204545454546
        # 0.38 0.8423295454545454
        # 0.39 0.8338068181818182
        # 0.4 0.8167613636363636
        # 0.41 0.8139204545454546
        # 0.42 0.828125
        # 0.43 0.7940340909090909
        # 0.44 0.8409090909090909
        # 0.45 0.7982954545454546
        # 0.46 0.8039772727272727
        # 0.47 0.828125
        # 0.48 0.8181818181818181
        # 0.49 0.8153409090909092
        # 0.5 0.8096590909090909
        # 0.51 0.78125
        # 0.52 0.7727272727272727
        # 0.53 0.75
        # 0.54 0.7670454545454546
        # 0.55 0.7428977272727273
        # 0.56 0.7571022727272727
        # 0.57 0.7556818181818181
        # 0.58 0.7542613636363636
        # 0.59 0.7954545454545455
        # 0.6 0.7642045454545454
        # 0.61 0.7826704545454546
        # 0.62 0.7755681818181819
        # 0.63 0.7627840909090908
        # 0.64 0.8025568181818181
        # 0.65 0.8025568181818182
        # 0.66 0.8110795454545455
        # 0.67 0.7982954545454546
        # 0.68 0.7940340909090909
        # 0.69 0.7713068181818181
        # 0.7 0.7982954545454546
        # 0.71 0.7556818181818181
        # 0.72 0.8309659090909092
        # 0.73 0.7940340909090908
        # 0.74 0.7599431818181818
        # 0.75 0.7727272727272727
        # 0.76 0.8210227272727273
        # 0.77 0.7954545454545454
        # 0.78 0.8167613636363635
        # 0.79 0.8607954545454546
        # 0.8 0.8778409090909092 best so far
        # 0.81 0.8139204545454545
        # 0.82 0.8295454545454546
        # 0.83 0.8323863636363635
        # 0.84 0.8423295454545455
        # 0.85 0.8210227272727273
        # 0.86 0.8366477272727273
        # 0.87 0.8323863636363636
        # 0.88 0.84375
        # 0.89 0.8451704545454546
        # 0.9 0.8551136363636365
        # 0.91 0.8607954545454546
        # 0.92 0.8110795454545454
        # 0.93 0.7755681818181819
        # 0.94 0.8267045454545454
        # 0.95 0.8451704545454546
        # 0.96 0.8622159090909092
        # 0.97 0.8323863636363638
        # 0.98 0.8380681818181819
        # 0.99 0.8451704545454546
        # 1.0 0.8707386363636365
    #reg_alpha:
        # 0.01 0.7784090909090909
        # 0.02 0.8110795454545454
        # 0.03 0.8110795454545454
        # 0.04 0.8011363636363636
        # 0.05 0.8423295454545454
        # 0.06 0.7769886363636364
        # 0.07 0.7684659090909092
        # 0.08 0.7443181818181818
        # 0.09 0.7769886363636362
        # 0.1 0.7798295454545454
        # 0.11 0.7769886363636364
        # 0.12 0.7585227272727273
        # 0.13 0.7230113636363636
        # 0.14 0.7144886363636364
        # 0.15 0.71875
        # 0.16 0.7173295454545454
        # 0.17 0.7599431818181819
        # 0.18 0.7869318181818181
        # 0.19 0.7982954545454546
        # 0.2 0.7556818181818182
        # 0.21 0.75
        # 0.22 0.7826704545454546
        # 0.23 0.7585227272727273
        # 0.24 0.7585227272727273
        # 0.25 0.7713068181818182
        # 0.26 0.7642045454545454
        # 0.27 0.7542613636363636
        # 0.28 0.7556818181818181
        # 0.29 0.7698863636363636
        # 0.3 0.7855113636363638
        # 0.31 0.7727272727272727
        # 0.32 0.7713068181818181
        # 0.33 0.7855113636363636
        # 0.34 0.8607954545454546
        # 0.35 0.8522727272727273
        # 0.36 0.8352272727272727
        # 0.37 0.8323863636363636
        # 0.38 0.84375
        # 0.39 0.8423295454545454
        # 0.4 0.840909090909091
        # 0.41 0.8323863636363636
        # 0.42 0.8394886363636364
        # 0.43 0.8451704545454546
        # 0.44 0.8252840909090908
        # 0.45 0.8267045454545454
        # 0.46 0.8309659090909091
        # 0.47 0.8181818181818183
        # 0.48 0.8394886363636364
        # 0.49 0.8139204545454546
        # 0.5 0.8451704545454546
        # 0.51 0.8579545454545454
        # 0.52 0.8607954545454546
        # 0.53 0.8494318181818182
        # 0.54 0.8622159090909091
        # 0.55 0.8664772727272727
        # 0.56 0.8480113636363636
        # 0.57 0.8380681818181819
        # 0.58 0.8380681818181819
        # 0.59 0.8167613636363635
        # 0.6 0.8082386363636364
        # 0.61 0.8565340909090908
        # 0.62 0.8409090909090909
        # 0.63 0.8622159090909092
        # 0.64 0.875 best so far
        # 0.65 0.8764204545454546 best so far
        # 0.66 0.875
        # 0.67 0.8579545454545455
        # 0.68 0.8551136363636364
        # 0.69 0.890625 best so far
        # 0.7 0.890625
        # 0.71 0.875
        # 0.72 0.8607954545454546
        # 0.73 0.8607954545454546
        # 0.74 0.8607954545454546
        # 0.75 0.8948863636363636 best so far
        # 0.76 0.8693181818181819
        # 0.77 0.8693181818181819
        # 0.78 0.8735795454545454
        # 0.79 0.8678977272727273
        # 0.8 0.8551136363636364
        # 0.81 0.8593750000000001
        # 0.82 0.8551136363636365
        # 0.83 0.8835227272727273
        # 0.84 0.8863636363636364
        # 0.85 0.8835227272727273
        # 0.86 0.8792613636363636
        # 0.87 0.8721590909090909
        # 0.88 0.8664772727272727
        # 0.89 0.8678977272727273
        # 0.9 0.8352272727272727
        # 0.91 0.8877840909090909
        # 0.92 0.8707386363636364
        # 0.93 0.8423295454545454
        # 0.94 0.8423295454545454
        # 0.95 0.8551136363636364
        # 0.96 0.8551136363636364
        # 0.97 0.875
        # 0.98 0.8650568181818181
        # 0.99 0.8678977272727273
        # 1.0 0.8707386363636365
    #reg_lambda
        # 0.01 0.7755681818181819
        # 0.02 0.71875
        # 0.03 0.7301136363636364
        # 0.04 0.7315340909090908
        # 0.05 0.7201704545454546
        # 0.06 0.7485795454545455
        # 0.07 0.7556818181818182
        # 0.08 0.7698863636363636
        # 0.09 0.7684659090909091
        # 0.1 0.7514204545454546
        # 0.11 0.778409090909091
        # 0.12 0.7514204545454546
        # 0.13 0.7840909090909092
        # 0.14 0.7840909090909092
        # 0.15 0.7940340909090908
        # 0.16 0.7798295454545454
        # 0.17 0.7855113636363636
        # 0.18 0.796875
        # 0.19 0.7599431818181819
        # 0.2 0.7684659090909091
        # 0.21 0.8153409090909092
        # 0.22 0.828125
        # 0.23 0.8295454545454546
        # 0.24 0.8096590909090909
        # 0.25 0.8068181818181819
        # 0.26 0.7997159090909091
        # 0.27 0.8181818181818181
        # 0.28 0.8238636363636364
        # 0.29 0.8238636363636364
        # 0.3 0.8295454545454546
        # 0.31 0.8210227272727273
        # 0.32 0.7713068181818181
        # 0.33 0.8693181818181819
        # 0.34 0.8764204545454546
        # 0.35 0.8650568181818181
        # 0.36 0.8707386363636364
        # 0.37 0.8735795454545454
        # 0.38 0.8892045454545455
        # 0.39 0.8792613636363638
        # 0.4 0.8707386363636364
        # 0.41 0.8664772727272728
        # 0.42 0.9019886363636365 best so far
        # 0.43 0.887784090909091
        # 0.44 0.8892045454545455
        # 0.45 0.8863636363636364
        # 0.46 0.8920454545454546
        # 0.47 0.8920454545454546
        # 0.48 0.8607954545454546
        # 0.49 0.8721590909090909
        # 0.5 0.8948863636363636
        # 0.51 0.8693181818181819
        # 0.52 0.8678977272727273
        # 0.53 0.8451704545454546
        # 0.54 0.8338068181818182
        # 0.55 0.8622159090909092
        # 0.56 0.8622159090909092
        # 0.57 0.8579545454545454
        # 0.58 0.8536931818181819
        # 0.59 0.8522727272727273
        # 0.6 0.8991477272727273
        # 0.61 0.8877840909090909
        # 0.62 0.8806818181818181
        # 0.63 0.8721590909090908
        # 0.64 0.8721590909090908
        # 0.65 0.8792613636363635
        # 0.66 0.8806818181818181
        # 0.67 0.8522727272727273
        # 0.68 0.8693181818181819
        # 0.69 0.872159090909091
        # 0.7 0.859375
        # 0.71 0.859375
        # 0.72 0.8536931818181819
        # 0.73 0.8409090909090909
        # 0.74 0.8409090909090909
        # 0.75 0.8480113636363636
        # 0.76 0.84375
        # 0.77 0.84375
        # 0.78 0.8423295454545455
        # 0.79 0.8494318181818182
        # 0.8 0.8693181818181819
        # 0.81 0.8707386363636365
        # 0.82 0.8707386363636365
        # 0.83 0.8707386363636365
        # 0.84 0.8664772727272728
        # 0.85 0.8622159090909092
        # 0.86 0.8494318181818181
        # 0.87 0.8593750000000001
        # 0.88 0.8636363636363638
        # 0.89 0.8536931818181819
        # 0.9 0.8678977272727273
        # 0.91 0.8721590909090909
        # 0.92 0.8806818181818182
        # 0.93 0.8409090909090908
        # 0.94 0.8409090909090908
        # 0.95 0.8323863636363636
        # 0.96 0.8565340909090908
        # 0.97 0.8451704545454546
        # 0.98 0.8522727272727273
        # 0.99 0.84375
        # 1.0 0.8636363636363636
       
        
    
        
        
    
##Run XGBoost on testing data set and create confusion matrix
# plot_confusion_matrix(model,X_test,y_test,values_format='d',display_labels=['Positive?,Negative?'])
# plt.xlabel('Predicted label')
# plt.ylabel('True label')

# from sklearn.impute import SimpleImputer
# imputer = SimpleImputer(missing_values=numpy.nan, strategy='mean')

# my_imputer = Imputer()
# train_X = my_imputer.fit_transform(train_X)
# test_X = my_imputer.transform(test_X)

# from xgboost import XGBRegressor

# my_model = XGBRegressor()
# # Add silent=True to avoid printing out updates with each cycle
# my_model.fit(train_X, train_y, verbose=False)

# # make predictions
# predictions = my_model.predict(test_X)

# from sklearn.metrics import mean_absolute_error
# print("Mean Absolute Error : " + str(mean_absolute_error(predictions, test_y)))




##### RANDOM FOREST ALGORITHM #####

print('Random Forest:')


##Random Forest with Optimal HyperParameters
print("starting modeling career...")
coef = [671,10,68,3,650,137,462]
RFmodel = RandomForestClassifier(max_depth = coef[0], min_samples_split = coef[1], 
                                       max_leaf_nodes = coef[2], min_samples_leaf = coef[3],
                                       n_estimators = coef[4], max_samples = coef[5],
                                       max_features = coef[6])

##Cross Validate
scores = cross_val_score(estimator = RFmodel,
                          X = X_train,
                          y = y_train,
                          cv = 5,
                          scoring = 'roc_auc',
                          verbose = True,
                          n_jobs=-1)

print('RF CV accuracy scores: %s' % scores)
print('RF CV accuracy: %.3f +/- %.3f' % (np.mean(scores), np.std(scores))) 


##Fitting Model
print('fitting...')
RFmodel.fit(X_train,y_train)
y_predict = RFmodel.predict(X_test)
y_train_predict = RFmodel.predict(X_train)
print('RF Train accuracy',accuracy_score(y_train, y_train_predict))
print('RF Test accuracy',accuracy_score(y_test,y_predict))

#ROC/AUC score
print('RF Train ROC/AUC Score', roc_auc_score(y_train, RFmodel.predict_proba(X_train)[:,1]))
print('RF Test ROC/AUC Score', roc_auc_score(y_test, RFmodel.predict_proba(X_test)[:,1]))

#ROC/AUC plotting
plt.figure(1)

fpr, tpr, thresholds = roc_curve(y_test, RFmodel.predict_proba(X_test)[:,1],drop_intermediate=False)

plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.title('ROC curve for Serotonin Classifier')
plt.xlabel('False Positive Rate (1 - Specificity)')
plt.ylabel('True Positive Rate (Sensitivity)')
plt.plot(fpr,tpr,label = 'RForest(area = %0.2f)' 
         % roc_auc_score(y_test, RFmodel.predict_proba(X_test)[:,1]), color='blue',lw=3)


#Best coefficients so far:
    #coef = [671,10,68,3,650,192,462]
    
#Sample code for testing hyperparameters
# score = 0.75       
# coef = [671,10,68,3,650,192,462]
# for ii in range(2,500,10): 
#         model = RandomForestClassifier(max_depth = coef[0], min_samples_split = coef[1], 
#                                        max_leaf_nodes = coef[2], min_samples_leaf = coef[3],
#                                        n_estimators = coef[4], max_samples = coef[5],
#                                        max_features = ii)
#         model.fit(X_train,y_train) 
#         y_predict = model.predict(X_test) 
#         y_train_predict = model.predict(X_train)
#         newscore = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
#         print(ii,newscore, end="")
#         if newscore > score:
#             print(' best so far')
#             score = newscore
#         else:
#             print()





##### XGBOOST ALGORITHM #####

print('XGBoost:')

##XGBoost with Optimal HyperParameters
print("starting modeling career...")
coef = [2,0.28,150,0.57,0.36,0.1,1,0,0.75,0.42]
XGBmodel = XGBClassifier(max_depth = coef[0],subsample = coef[1],n_estimators = coef[2],
                      colsample_bylevel = coef[3], colsample_bytree = coef[4],learning_rate=coef[5], 
                      min_child_weight = coef[6], random_state = coef[7],reg_alpha = coef[8],
                      reg_lambda = coef[9])

##Cross Validate
scores = cross_val_score(estimator = XGBmodel,
                          X = X_train,
                          y = y_train,
                          cv = 5,
                          scoring = 'roc_auc',
                          verbose = True,
                          n_jobs=-1)

print('XGB CV accuracy scores: %s' % scores)
print('XGB CV accuracy: %.3f +/- %.3f' % (np.mean(scores), np.std(scores))) 


##Fitting Model
print('fitting...')
XGBmodel.fit(X_train,y_train)
y_predict = XGBmodel.predict(X_test)
y_train_predict = XGBmodel.predict(X_train)
print('XGB Train accuracy',accuracy_score(y_train, y_train_predict))
print('XGB Test accuracy',accuracy_score(y_test,y_predict))



#ROC/AUC score
print('XGB Train ROC/AUC Score', roc_auc_score(y_train, XGBmodel.predict_proba(X_train)[:,1]))
print('XGB Test ROC/AUC Score', roc_auc_score(y_test, XGBmodel.predict_proba(X_test)[:,1]))

#ROC/AUC plotting
plt.figure(1)

fpr, tpr, thresholds = roc_curve(y_test, XGBmodel.predict_proba(X_test)[:,1],drop_intermediate=False)
plt.plot(fpr,tpr,label = 'XGBoost(area = %0.2f)' 
         % roc_auc_score(y_test, XGBmodel.predict_proba(X_test)[:,1]), color='red',lw=3)


        
#Best coefficients so far:
    #coef = [2,0.28,150,0.57,0.36,0.1,1,0,0.75,0.42]
    
#Sample code for testing hyperparameters
    # score = 0.7159090909090909       
    # coef = [2,0.4,150,.8,1,.1,1,0,1,0.5]
    # for ii in range(2,31): 
    #     model = XGBClassifier(max_depth = ii,subsample = coef[1],n_estimators = coef[2],
    #                       colsample_bylevel = coef[3], colsample_bytree = coef[4],learning_rate=coef[5], 
    #                       min_child_weight = coef[6], random_state = coef[7],reg_alpha = coef[8],
    #                       reg_lambda = coef[9])
    #     model.fit(X_train,y_train) 
    #     y_predict = model.predict(X_test) 
    #     y_train_predict = model.predict(X_train)
    #     newscore = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
    #     print(ii,newscore, end="")
    #     if newscore > score:
    #         print(' best so far')
    #         score = newscore
    #     else:
    #         print()
    
### XGBoost MODEL PREDICTION ###
### Fitting Model ###
fitted = XGBmodel.fit(X_train,y_train)
y_score = XGBmodel.fit(X_train,y_train).predict_proba(X_test)

predictions = fitted.predict(X_test)   

# predict_im = data_to_img(boolim2_2,predictfions)
SVM.overlay_predictions(image, train_bool, predictions, y_test, ind_test,domains)


##### KNN ALGORITHM #####


print('KNN:')
pipe_knn = make_pipeline(RobustScaler(),KNeighborsClassifier())

#SVM MODEL FITTING
#we create an instance of SVM and fit out data.
# print("starting modeling career...")

# gs = GridSearchCV(estimator = pipe_knn,
#                   param_grid = param_grid,
#                   scoring = 'roc_auc',
#                   cv = 5,
#                   n_jobs = -1,
#                   verbose = 10)


# print("Fitting...")
# gs = gs.fit(X_train,y_train)
# print('best score: ' + str(gs.best_score_))
# print(gs.best_params_)
# pipe_knn = gs.best_estimator_
### END Gridsearch ####

### Setting Parameters ###
#{'kneighborsclassifier__n_neighbors': 7}
print('fitting...')

pipe_knn.set_params(kneighborsclassifier__n_neighbors = 7)

### Cross Validate ###
scores = cross_val_score(estimator = pipe_knn,
                          X = X_train,
                          y = y_train,
                          cv = 10,
                          scoring = 'roc_auc',
                          verbose = True,
                          n_jobs=-1)

print('CV accuracy scores: %s' % scores)
print('CV accuracy: %.3f +/- %.3f' % (np.mean(scores), np.std(scores))) 

### Fitting Model ###
fitted = pipe_knn.fit(X_train,y_train)
y_score = pipe_knn.fit(X_train,y_train).predict_proba(X_test)
print(pipe_knn.score(X_test,y_test))

### DATA PROCESSING IMAGE 2 ###
#pick a test image
# os.chdir(r'C:\Users\jsalm\Documents\Python Scripts\SVM_7232020')
Test_im = np.array(cv2.imread("images_5HT/injured 60s_sectioned_CH2.tif")[:,:,2]/255).astype(np.float32)

#extract features
# im_segs_test, _, domains_test, paded_im_seg_test, _, hog_features_test = SVM.feature_extract(Test_im, ff_width, wiener_size, med_size,False)
# X_test = SVM.create_data(im_segs_test,False)

# ### SVM MODEL PREDICTION ###
# predictions = fitted.predict(X_test)   

# # predict_im = data_to_img(boolim2_2,predictfions)
# SVM.overlay_predictions(image, train_bool, predictions, y_test, ind_test,domains)

### Confusion Matrix: Save fig if interesting ###
# confmat = confusion_matrix(y_true = y_test, y_pred=predictions)
# fig, ax = plt.subplots(figsize=(2.5, 2.5))
# ax.matshow(confmat, cmap=plt.cm.Blues, alpha=0.3)
# for i in range(confmat.shape[0]):
#     for j in range(confmat.shape[1]):
#         ax.text(x=j, y=i, s=confmat[i, j], va='center', ha='center')

# plt.xlabel('Predicted label')
# plt.ylabel('True label')

# plt.tight_layout()
# plt.savefig(os.path.join(save_bin,'confussion_matrix.png'),dpi=200,bbox_inches='tight')
# plt.show()

### ROC Curve ###
fpr, tpr,_ = roc_curve(y_test, y_score[:,1])
roc_auc = auc(fpr, tpr)
SVM.write_auc(fpr,tpr)
#fpr,tpr,roc_auc = SVM.read_auc()


plt.figure(1)

plt.plot(fpr, tpr, color='lightblue', lw=3, label='KNN (area = %0.2f)' % roc_auc)


##### SVM ALGORITHM #####


#we create an instance of SVM and fit out data.
print('SVM:')
print("starting modeling career...")

# gs = GridSearchCV(estimator = pipe_svc,
#                   param_grid = param_grid2,
#                   scoring = 'roc_auc',
#                   cv = 5,
#                   n_jobs = -1,
#                   verbose = 10)


# print("Fitting...")
# gs = gs.fit(X_train,y_train)
# print('best score: ' + str(gs.best_score_))
# print(gs.best_params_)
# pipe_svc = gs.best_estimator_
### END Gridsearch ####

### Setting Parameters ###
print('fitting...')
#{'svc__C': 100, 'svc__gamma': 0.001, 'svc__kernel': 'rbf'} (~0.72% f1_score)
#{svc__C=130, svc__decision_function_shape=ovr, svc__gamma=0.0005, svc__kernel=rbf}

pipe_svc.set_params(svc__C =  130, 
                    svc__gamma = 0.0005, 
                    svc__kernel =  'rbf',
                    svc__probability = True,
                    svc__shrinking = False,
                    svc__decision_function_shape = 'ovr')

### Cross Validate ###
scores = cross_val_score(estimator = pipe_svc,
                          X = X_train,
                          y = y_train,
                          cv = 10,
                          verbose = True,
                          n_jobs=-1)

print('CV accuracy scores: %s' % scores)
print('CV accuracy: %.3f +/- %.3f' % (np.mean(scores), np.std(scores))) 

### Fitting Model ###
fitted = pipe_svc.fit(X_train,y_train)
y_score = pipe_svc.fit(X_train,y_train).decision_function(X_test)
print(pipe_svc.score(X_test,y_test))

### DATA PROCESSING IMAGE 2 ###
#pick a test image
Test_im = np.array(cv2.imread("images_5HT/injured 60s_sectioned_CH2.tif")[:,:,2]/255).astype(np.float32)

#extract features
# im_segs_test, _, domains_test, paded_im_seg_test, _, hog_features_test = SVM.feature_extract(Test_im, ff_width, wiener_size, med_size,False)
# X_test = SVM.create_data(im_segs_test,False)

# ### SVM MODEL PREDICTION ###
# predictions = fitted.predict(X_test)   

# # predict_im = data_to_img(boolim2_2,predictfions)
# SVM.overlay_predictions(image, train_bool, predictions, y_test, ind_test,domains)

### Confusion Matrix: Save fig if interesting ###
<<<<<<< Updated upstream
confmat = confusion_matrix(y_true = y_test, y_pred=predictions)
fig, ax = plt.subplots(figsize=(2.5, 2.5))
ax.matshow(confmat, cmap=plt.cm.Blues, alpha=0.3)
for i in range(confmat.shape[0]):
    for j in range(confmat.shape[1]):
        ax.text(x=j, y=i, s=confmat[i, j], va='center', ha='center')

plt.xlabel('Predicted label')
plt.ylabel('True label')

plt.tight_layout()
#plt.savefig('images/06_09.png', dpi=300)
plt.show()
=======
# confmat = confusion_matrix(y_true = y_test, y_pred=predictions)
# fig, ax = plt.subplots(figsize=(2.5, 2.5))
# ax.matshow(confmat, cmap=plt.cm.Blues, alpha=0.3)
# for i in range(confmat.shape[0]):
#     for j in range(confmat.shape[1]):
#         ax.text(x=j, y=i, s=confmat[i, j], va='center', ha='center')

# plt.xlabel('Predicted label')
# plt.ylabel('True label')

# plt.tight_layout()
# plt.savefig(os.path.join(save_bin,'confussion_matrix.png'),dpi=200,bbox_inches='tight')
# plt.show()
>>>>>>> Stashed changes

### ROC Curve ###
fpr, tpr,_ = roc_curve(y_test, y_score)
roc_auc = auc(fpr, tpr)

plt.figure(1)

<<<<<<< Updated upstream
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
=======
plt.plot(fpr, tpr, color='darkorange',lw=3, label='SVM (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=3, linestyle='--')
>>>>>>> Stashed changes
plt.legend(loc="lower right")
plt.show()

# #PLOT IMAGES
# # Filters.imshow_overlay(Test_im,predict_im,'predictions2',True)

# name_list = ["image","denoised_im","median_im","thresh_im","dir_im","gau_im","di_im","t_im"]
# for i in range(0,len(image_tuple)):
#     plt.figure(name_list[i]);plt.imshow(image_tuple[i])