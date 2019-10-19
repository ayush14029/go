"""
tester - it takes an input file containing a commit sample from 2 users and helps determine the final directory based relevance scores assigned to them.
Needs atleast two commits from different users in the same directory to compare their influence and ranking.
Run the program as: python3 gitRanker.py tester (arg1) input_file (arg2) directory_path (arg3)

trainer - it simply retrains the whole program again, periodic has to  be done to keeep the system updated
Run the program as: python3 gitRanker.py trainer (arg1)

ranker - this just directly outputs the rank for the user's choice of a folder based on currently trained data.
Run the program as: python3 gitRanker.py ranker (arg1) folder_path (arg2)

feature_selector - this takes in a weight argument to decide a new weighting for the features including 0 as an option. Trains the network agan
with the new weights
Run the program as: python3 gitRanker.py ranker (arg1) weight_dict_JsonFile (arg2)
sample weight dict json file - {"files_length":1e-7,"file_count":0.0055,"relative_added":0.0017,"relative_deleted":0.0007,"commit_count":0.00125,"relative_directory_contr":1}
Specify weights for all features, including 0 if feature is not needed
"""

import os
import subprocess 
import sys
import re
import datetime
import pickle
import statistics
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pdb
import itertools
from utilities import *
from dirWalk import *
from rankMain import *
import warnings

def warn(*args, **kwargs):
    pass
warnings.warn = warn

arg1 = sys.argv[1]
if len (sys.argv) > 2:
	arg2 = sys.argv[2]

def build_dict_data_file(run_arg):
	if os.path.exists('final_dir_data'):
		if run_arg == "tester":
			with open('new_commit_data') as json_file:
				data_from_commit = json.load(json_file)
			dic_df_new_commit = {}
			for item in data_from_commit:
				dic_df_new_commit[item] = pd.DataFrame.from_dict(data_from_commit[item]).transpose()

			return dic_df_new_commit

		else:
			with open('final_dir_data') as json_file:
			    final_dir_data = json.load(json_file)

			dic_df_data = {}
			for item in final_dir_data:
				dic_df_data[item] = pd.DataFrame.from_dict(final_dir_data[item]).transpose()

			return dic_df_data
	else:
		print ("model has never been trained, run trainer")

if arg1 == "feature_selector":
	dic_df_data = build_dict_data_file(arg1)
	with open('weight_dict.json') as json_file:
		new_weights = json.load(json_file)
	dic_df_data_prob = rank_appear_prob (dic_df_data, new_weights)
	train_p, train_r, train_a, test_p, test_r, test_a = training(dic_df_data_prob)
	print ("Successfully changed the model weights")
	print ("New metrics are (train precision, train recall, train accuracy, test precision, test recall, test accuracy")
	print (str(train_p), str(train_r), str(train_a), str (test_p), str(test_r), str(test_a))
	exit(0)

if arg1 == 'trainer':
	lines = subprocess.check_output(['git', 'log', '-p', '--', './src'], stderr=subprocess.STDOUT).decode(sys.stdout.encoding,  errors = "replace").splitlines()
	process_commits (lines, arg1)
	dic_df_data = build_dict_data_file(arg1)
	dic_df_data_prob = rank_appear_prob (dic_df_data)
	train_p, train_r, train_a, test_p, test_r, test_a = training(dic_df_data_prob)
	print ("Metrics are (train precision, train recall, train accuracy, test precision, test recall, test accuracy")
	print (str(train_p), str(train_r), str(train_a), str (test_p), str(test_r), str(test_a))
	exit(0)

pkl_filename = "trained_model_dic.pkl"
if sys.argv[1] == 'ranker':
	if os.path.exists(pkl_filename):
		with open(pkl_filename, 'rb') as file:
			pickle_model = pickle.load(file)
		dic_df_data = build_dict_data_file(arg1)
		dic_df_data_prob = rank_appear_prob (dic_df_data)
		path = sys.argv[2]
		ranker(dic_df_data_prob, path, pickle_model[path])
	else:
		print ("Please train the model first")

	exit(0)


if arg1 == 'tester':
	if os.path.exists(pkl_filename):
		f = open(arg2, 'rb')
		lines = f.read().decode(sys.stdout.encoding,  errors = "replace").splitlines()
		process_commits (lines, arg1)
		dic_df_data = build_dict_data_file(arg1)
		dic_df_data_prob = rank_appear_prob (dic_df_data)
		with open(pkl_filename, 'rb') as file:
			pickle_model = pickle.load(file)
		testing(dic_df_data_prob, pickle_model[sys.argv[3]])
	else:
		print ("Please train the model first")