import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression
import pdb
from sklearn.metrics import *
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import itertools
import json
import pickle

class User:
    def __init__(self, id):
        self.id = id
        self.positive = []
        self.negative = []
        
    def add_positive(self, movie_id):
        self.positive.append(movie_id)
    
    def add_negative(self, movie_id):
        self.negative.append(movie_id)
    
    def get_positive(self):
        return self.positive
    
    def get_negative(self):
        return self.negative



np.random.seed(1)

class EventsGenerator:
    NUM_OF_USERS = 1

    def __init__(self, learning_data, buy_probability, opened):
        self.learning_data = learning_data
        self.buy_probability = buy_probability
        self.users = []
        self.NUM_OF_OPENED_MOVIES_PER_USER = opened
        for id in range(1, self.NUM_OF_USERS+1):
            self.users.append(User(id))
        
    def run(self, pairwise=False):
        # print (self.users, "hellp")
        for user in self.users:
            # print (self.learning_data.index)
            opened_movies = np.random.choice(self.learning_data.index.values, self.NUM_OF_OPENED_MOVIES_PER_USER)
            self.__add_positives_and_negatives_to(user, opened_movies)

        return self.__build_events_data()

    def __add_positives_and_negatives_to(self, user, opened_movies):
        # print (opened_movies)
        for movie_id in opened_movies:

            if np.random.binomial(1, self.buy_probability.loc[movie_id]): 
                user.add_positive(movie_id)
            else:
                user.add_negative(movie_id)
                
    def __build_events_data(self):
        events_data = []
        
        for user in self.users:
            for positive_id in user.get_positive():
                # print(positive_id)
                tmp = self.learning_data.loc[positive_id].to_dict()
                tmp['outcome'] = 1
                events_data += [tmp]
            
            for negative_id in user.get_negative():
                tmp = self.learning_data.loc[negative_id].to_dict()
                tmp['outcome'] = 0
                events_data += [tmp]
        # print(events_data) 
        return pd.DataFrame(events_data)


def build_learning_data_from(movie_data):
    feature_columns = np.setdiff1d(movie_data.columns, np.array(['top_prob']))
    learning_data = movie_data.loc[:, feature_columns]
    
    scaler = StandardScaler()
    for i in range(feature_columns.shape[0]):
        learning_data[feature_columns[i]] = scaler.fit_transform(learning_data[[feature_columns[i]]])
    
    return learning_data, feature_columns


def get_test_train_data(events_data, feature_columns):
    X = events_data.loc[:, feature_columns].values.astype(np.float32)

    y = events_data.loc[:, ['outcome']].values.astype(np.float32).ravel()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return [X_train, X_test, y_train, y_test]


def get_predicted_outcome(model, data):
    return np.argmax(model.predict_proba(data), axis=1).astype(np.float32)


def get_predicted_rank(model, data):
    return model.predict_proba(data)[:, 1]

def train_model(model, prediction_function, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    
    y_train_pred = prediction_function(model, X_train)

    # print('train precision: ' + str(precision_score(y_train, y_train_pred)))
    # print('train recall: ' + str(recall_score(y_train, y_train_pred)))
    # print('train accuracy: ' + str(accuracy_score(y_train, y_train_pred)))

    y_test_pred = prediction_function(model, X_test)

    # print('test precision: ' + str(precision_score(y_test, y_test_pred)))
    # print('test recall: ' + str(recall_score(y_test, y_test_pred)))
    # print('test accuracy: ' + str(accuracy_score(y_test, y_test_pred)))
    
    return model, precision_score(y_train, y_train_pred), recall_score(y_train, y_train_pred), accuracy_score(y_train, y_train_pred),\
    precision_score(y_test, y_test_pred), recall_score(y_test, y_test_pred), accuracy_score(y_test, y_test_pred)

def decide_rank(model, learning_data, predict_fun):
    lg_input = learning_data.values.astype(np.float32)
    # print('overall input shape: ' + str(lg_input.shape))

    learning_data_with_rank = learning_data.copy()
    learning_data_with_rank['rank'] = predict_fun(model, lg_input)
    return learning_data_with_rank