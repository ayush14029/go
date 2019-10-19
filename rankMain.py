import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression
import pdb
import pickle
from sklearn.metrics import *
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import itertools
import json
from utilities import *

def_weights = {"files_length" : 1/10000000, "file_count" : 1/180, "relative_added" : 1/600, "relative_deleted" : 1/1500, "commit_count" : 1/800, "relative_directory_contr" : 1}


def rank_appear_prob(dic_df_data, weights = def_weights):
	for item in dic_df_data:
			dic_df_data[item]['top_prob'] = dic_df_data[item]["files_length"] * weights["files_length"] + dic_df_data[item]["file_count"] * weights["file_count"] + \
			dic_df_data[item]["commit_count"] * weights["commit_count"] + dic_df_data[item]["relative_added"] * weights["relative_added"] + \
			dic_df_data[item]["relative_directory_contr"] * weights["relative_directory_contr"] + dic_df_data[item]["relative_deleted"] * weights["relative_deleted"]

	for item in dic_df_data:
		dic_df_data[item]["top_prob"] -= dic_df_data[item]["top_prob"].min()
		if  dic_df_data[item]["top_prob"].max() == 0:
			dic_df_data[item]["top_prob"] = 0
		else:
			dic_df_data[item]["top_prob"] /= dic_df_data[item]["top_prob"].max()

	return dic_df_data


def testing (dic_df_data, model):
	for item in dic_df_data:
		print(dic_df_data[item])
		learning_data, feature_cols = build_learning_data_from(dic_df_data[item])
		output_data = decide_rank(model, learning_data, get_predicted_rank)
		print (output_data)

def training (dic_df_data):
	model = {}
	train_p = 0
	train_r = 0
	train_a = 0
	test_p = 0
	test_r = 0
	test_a = 0
	count = 0
	for item in dic_df_data:
		learning_data, feature_cols = build_learning_data_from(dic_df_data[item])
		events_data = EventsGenerator(learning_data, dic_df_data[item]['top_prob'], learning_data.size).run()
		X_train, X_test, y_train, y_test = get_test_train_data(events_data, feature_cols)
		if y_train.tolist().count(1) < 1:
			print ("rank cannot be found for this dir " + item)
			print
			continue
		model[item], trp, trr, tra, tep, ter, tea = train_model(LogisticRegression(), get_predicted_outcome, X_train, y_train, X_test, y_test)
		train_p+=trp
		train_r+=trr
		train_a+=tra
		test_p+=tep
		test_r+=ter
		test_a+=tea
		count+=1

	pkl_filename = "trained_model_dic.pkl"
	with open(pkl_filename, 'wb') as file:
	    pickle.dump(model, file)

	return train_p/count, train_r/count, train_a/count, test_p/count, test_r/count, test_a/count

def ranker (dic_df_data, path, model):
	learning_data, feature_cols = build_learning_data_from(dic_df_data[path])
	output_data = decide_rank(model, learning_data, get_predicted_rank)
	print(path)
	print (output_data.nlargest(5, 'rank'))