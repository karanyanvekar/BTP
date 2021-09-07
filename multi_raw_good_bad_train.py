# -*- coding: utf-8 -*-
"""Copy of NSCLC_raw_multi_good_bad.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AZEzJvKKen6gzZnLBopHdvyF2rDtgbmV
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
import tensorflow.keras.optimizers as optimizer
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

gpu_id=1
if len(tf.config.list_physical_devices('GPU'))!=0: # If GPU is available
    gpus = tf.config.experimental.list_physical_devices('GPU')# Lists all available GPUs
    tf.config.experimental.set_visible_devices(gpus[gpu_id], 'GPU')# Forces it to use only gpu gpu_id
    tf.config.experimental.set_memory_growth(gpus[gpu_id], True)# Forces Tensorflow to use as much memory as needed
else:
    print("No GPUs found. Running on CPU")

data_file = '../NSCLC_raw_multi_op_complete.csv'
print("Process 1")
data = pd.read_csv(data_file, index_col=0)

data = data.transpose()

Label_File = '../NSCLC_TCGA_clinical_op_complete_good_bad.csv'

Labels = pd.read_csv(Label_File, index_col=0)

Labels.drop(Labels[Labels['Group'] == 'Intermediate'].index, inplace=True)

data = pd.merge(data, Labels['Group'], how = 'inner', left_index=True, right_index=True)

data = data.fillna(0)

X = data.iloc[:, 0:-1]
Y = data.iloc[:, -1]
print("Process 2")
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 69)

Y_train = (Y_train == 'Good')

Y_test = (Y_test == 'Good')

Y_train = np.multiply(Y_train, 1)

Y_test = np.multiply(Y_test, 1)
print("Process 3")
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled = scaler.fit_transform(X_train)
scaled = pd.DataFrame(scaled)
scaled.index = X_train.index
X_train_Z = scaled

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaled = scaler.fit_transform(X_test)
scaled = pd.DataFrame(scaled)
scaled.index = X_test.index
X_test_Z = scaled

X_train_Z = X_train_Z.fillna(0)
X_test_Z = X_test_Z.fillna(0)

# from pandas import read_csv
# from sklearn.model_selection import cross_val_score
# from sklearn.svm import SVC
# from sklearn.model_selection import RepeatedStratifiedKFold
# from skopt import BayesSearchCV
# params = dict()
# params['C'] = (1e-6, 100.0, 'log-uniform')
# params['gamma'] = (1e-6, 100.0, 'log-uniform')
# params['degree'] = (1,5)
# params['kernel'] = ['linear', 'poly', 'rbf', 'sigmoid']
# # define evaluation
# cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
# # define the search
# search = BayesSearchCV(estimator=SVC(), search_spaces=params, n_jobs=-1, cv=cv)
# # perform the search
# search.fit(X_train_Z, Y_train)
# # report the best result
# print(search.best_score_)
# print(search.best_params_)

# Y_predict = search.predict(X_test_Z)
# print("Accuracy:",metrics.accuracy_score(Y_test, Y_predict))
# print("Precision:",metrics.precision_score(Y_test, Y_predict))
# print("Recall:",metrics.recall_score(Y_test, Y_predict))
# from sklearn.metrics import classification_report, confusion_matrix
# print(confusion_matrix(Y_test, Y_predict))
print("Process 4")
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Create a Random Forest Classifier
rf = RandomForestClassifier()

# Hyperparameter Optimization
parameters = {'n_estimators': [4, 6, 9, 10, 15], 
              'max_features': ['log2', 'sqrt','auto'], 
              'criterion': ['entropy', 'gini'],
              'max_depth': [2, 3, 5, 10], 
              'min_samples_split': [2, 3, 5],
              'min_samples_leaf': [1, 5, 8]
             }

# Run the grid search
grid_obj = GridSearchCV(rf, parameters)
grid_obj = grid_obj.fit(X_train_Z, Y_train)

# Set the rf to the best combination of parameters
rf = grid_obj.best_estimator_

# Train the model using the training sets 
rf.fit(X_train_Z, Y_train)
Y_predict = rf.predict(X_train_Z)
print("RANDOM FOREST")
print("Accuracy:",metrics.accuracy_score(Y_train, Y_predict))
print("Precision:",metrics.precision_score(Y_train, Y_predict))
print("Recall:",metrics.recall_score(Y_train, Y_predict))
from sklearn.metrics import classification_report, confusion_matrix
print(confusion_matrix(Y_train, Y_predict))
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import GaussianNB
nb_classifier = GaussianNB()

params_NB = {'var_smoothing': np.logspace(0,-9, num=100)}
gs_NB = GridSearchCV(estimator=nb_classifier, 
                 param_grid=params_NB, 
                 verbose=1, 
                 scoring='accuracy') 
gs_NB.fit(X_train_Z, Y_train)

print(gs_NB.best_params_) 
Y_predict = gs_NB.predict(X_train_Z)
print("GAUSSIAN NAIVE BAYES")
print("Accuracy:",metrics.accuracy_score(Y_train, Y_predict))
print("Precision:",metrics.precision_score(Y_train, Y_predict))
print("Recall:",metrics.recall_score(Y_train, Y_predict))
from sklearn.metrics import classification_report, confusion_matrix
print(confusion_matrix(Y_train, Y_predict))
print("Done")
