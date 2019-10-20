## GitRanker: Rank users in a directory based on their commit activity.

The aim of this project was to build a robust system for repository based ranking of users on github taking into account their commit activity corresponding to the said repository. The output of the ranker is a table of the top 5 users with their email and rank score assigned to theem via the model. The training and testing data for the LR model are taken as a random split from the commits currently logged and the weights of the model can be altered to train it again via the feature_selector functionality.

If the trained model is deleted from the repository, one has to necessariily run the trainer/feature_selector script first before moving forward to ranker or tester. The parent file to. run all the operations given below is gitRank.py. 

There are four possible operations one can perform. They are explained in detail below:

1. ranker - this just directly outputs the rank for the user's choice of a folder based on currently trained data.
Run the program as: `python3 gitRanker.py ranker (arg1) <folder_path> (arg2)`

2. tester - it takes an input file containing a commit sample from 2 users and helps determine the final directory based relevance scores assigned to them.
Needs atleast two commits from different users in the same directory to compare their influence and ranking.
Run the program as: `python3 gitRanker.py tester (arg1) <input_file> (arg2) <directory_path> (arg3)`

3. trainer - it simply retrains the whole program again, periodic has to  be done to keeep the system updated
Run the program as: `python3 gitRanker.py trainer (arg1)` 

4. feature_selector - this takes in a weight argument to decide a new weighting for the features including 0 as an option. Trains the network again with the new weights.
Run the program as: `python3 gitRanker.py ranker (arg1) <weight_dict_JsonFile> (arg2)`

sample - [weight_dict.json](https://github.com/ayush14029/go/blob/master/weight_dict.json)

{"files_length":1e-7,"file_count":0.0055,"relative_added":0.0017,"relative_deleted":0.0007,"commit_count":0.00125,"relative_directory_contr":1}

Specify weights for all features, including 0 if feature is not needed

** Note: For some directories (About 200/900), there might be too few training/testing samples to determine a legitimate ranking of the users and the commits in the particular directory. Additionally, these also include some directories which no longer exist due to. further. commits. In such a cases the rankings are not provided **

The following diagram explores the construction of the ranking function, the training of the Learning to Rank Model and the testing
performed against the metrics:

![](gitRankArch.png)
