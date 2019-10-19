import os
import subprocess
import re
import datetime
import pickle
import statistics
import json

leading_4_spaces = re.compile('^    ')

def process_commits(lines, run_arg):
	commits = []
	current_commit = {}
	count = 0
	def save_current_commit():
		title = current_commit['message'][0]
		message = current_commit['message'][1:]
		actual_message = []
		if message:
			for i in range(len(message)):
				if message[i] == '':
					continue
				elif message[i].startswith('Reviewed-by'):
					key, value = message[i].split(':', 1)
					current_commit['reviewedBy'] = value.strip()

				elif message[i].startswith('Reviewed-on'):
					continue

				elif message[i].startswith('Change-Id'):
					continue

				elif message[i].startswith('Run-TryBot'):
					continue

				elif message[i].startswith('TryBot-Result'):
					continue

				else:
					actual_message.append(message[i])

		current_commit['title'] = title
		current_commit['message'] = ' '.join(actual_message)
		commits.append(current_commit)

	#.  still have to include the filee which has been acted upon

	for line in lines:
		if not line.startswith('   '):
			if line.startswith('commit '):
				if current_commit:
					count+=1
					if "added_content" in current_commit:
						' '.join(current_commit["added_content"])
						if "files_length" in current_commit:
							current_commit["relative_added"] = len(current_commit["added_content"]) / current_commit["files_length"]
						else:
							current_commit["relative_added"] = 0

					if "deleted_content" in current_commit:
						' '.join(current_commit["deleted_content"])
						if "files_length" in current_commit:
							current_commit["relative_deleted"] = len(current_commit["deleted_content"]) / current_commit["files_length"] 
						else:
							current_commit["relative_deleted"] = 0
						if "TODO" in current_commit["deleted_content"] or "todo" in current_commit["deleted_content"]:
							current_commit['todo'] = current_commit['deleted_content'].lower().count('todo')
						else:
							current_commit['todo'] = 0
					# print (count)
					save_current_commit()
					current_commit = {}
				current_commit['hash'] = line.split('commit ')[1]


			elif line.startswith('Author'):
				try:
					key, value = line.split(':', 1)
					current_commit[key.lower()] = value.strip()
				except ValueError:
					pass

			elif line.startswith('Date'):
				try:
					key, value = line.split(':', 1)
					current_commit[key.lower()] = value.strip()
				except ValueError:
					pass

			elif line.startswith('diff'):
				current_commit['directory'] = '/'.join(line.split(' ')[2].split('/')[1:-1])
				current_commit.setdefault('files', [])
				f = '/'.join(line.split(' ')[2].split('/')[1:])
				if f not in current_commit['files']:
					try:
						with open(f) as fh:
							for i, l in enumerate(fh):
								pass
						if "files_length" in current_commit:
							current_commit["files_length"]+=(i+1)
						else:
							current_commit["files_length"] = (i+1)

						if "file_count" in current_commit:
							current_commit["file_count"]+=1
						else:
							current_commit["file_count"] = 1
						current_commit['files'].append(f)
					except:
						pass
				# current_commit.setdefault('files', []).append('/'.join(line.split(' ')[2].split('/')[1:]))

			elif len(line)>1 and line[0] == '+' and line[1]!='+':
				current_commit.setdefault('added_content', []).append(leading_4_spaces.sub('', line))

			elif len(line)>1 and line[0] == '-' and line[1]!='-':
				current_commit.setdefault('deleted_content', []).append(leading_4_spaces.sub('', line))


		else:
			current_commit.setdefault('message', []).append(leading_4_spaces.sub('', line))

	if current_commit:
		count+=1
		if "added_content" in current_commit:
			' '.join(current_commit["added_content"])
			if "files_length" in current_commit:
				current_commit["relative_added"] = len(current_commit["added_content"]) / current_commit["files_length"]
			else:
				current_commit["relative_added"] = 0

		if "deleted_content" in current_commit:
			' '.join(current_commit["deleted_content"])
			if "files_length" in current_commit:
				current_commit["relative_deleted"] = len(current_commit["deleted_content"]) / current_commit["files_length"] 
			else:
				current_commit["relative_deleted"] = 0
			if "TODO" in current_commit["deleted_content"] or "todo" in current_commit["deleted_content"]:
				current_commit['todo'] = current_commit['deleted_content'].lower().count('todo')
			else:
				current_commit['todo'] = 0
		# print (count)
		save_current_commit()
		current_commit = {}

	print ("Sample info extraction from commit")
	print
	print (commits[0])

	with open("test.txt", "wb") as fp:
		pickle.dump(commits, fp)
	with open("test.txt", "rb") as fp:
		commits = pickle.load(fp)

	parent_dic = {}
	directories = {}
	authors = {}

	for item in commits:
		commit_year = item["date"].split()[4]
		time_difference = 2020 - int(commit_year)
		if "directory" not in item:
			continue
		cpt = sum([len(files) for r, d, files in os.walk(item['directory'])])
		if item['directory'] not in directories:
			directories[item['directory']] = len(directories) + 1

		if item['author'] not in authors:
			authors[item['author']] = len(authors) + 1

		if item['directory'] in parent_dic:
			if item["author"] in parent_dic[item['directory']]:
				if "files_length" in parent_dic[item['directory']][item["author"]]:
					if "files_length" in item:
						parent_dic[item['directory']][item["author"]]["files_length"] += (item["files_length"] * 2**(-1* time_difference/10))
				if "file_count" in parent_dic[item['directory']][item["author"]]:
					if "file_count" in item:
						parent_dic[item['directory']][item["author"]]["file_count"] += (item["file_count"] * 2**(-1* time_difference/10) / (cpt+1))
				if "relative_added" in parent_dic[item['directory']][item["author"]]:
					if "relative_added" in item:
						parent_dic[item['directory']][item["author"]]["relative_added"] += (item["relative_added"] * 2**(-1* time_difference/10))
				if "relative_deleted" in parent_dic[item['directory']][item["author"]]:
					if "relative_deleted" in item:
						parent_dic[item['directory']][item["author"]]["relative_deleted"] += (item["relative_deleted"] * 2**(-1* time_difference/10))

				if "commit_count" in parent_dic[item['directory']][item["author"]]:
					parent_dic[item['directory']][item["author"]]["commit_count"]+=1

				if "commit_size" in parent_dic[item['directory']][item['author']]:
					if "added_content" in item:
						if "deleted_content" in item:
							parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content']) + len(item['deleted_content'])* 2**(-1* time_difference/10))
						else:
							parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content'])* 2**(-1* time_difference/10))
					else:
						if "deleted_content" in item:
							parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['deleted_content'])* 2**(-1* time_difference/10))
						else:
							parent_dic[item['directory']][item['author']]['commit_size'].append(0)

			else:
				parent_dic[item['directory']][item['author']] = {}
				if "files_length" in item:
					parent_dic[item['directory']][item["author"]]["files_length"] = (item["files_length"] * 2**(-1* time_difference/10))
				else:
					parent_dic[item['directory']][item["author"]]["files_length"] = 0
				if "file_count" in item:
					parent_dic[item['directory']][item["author"]]["file_count"] = (item["file_count"] * 2**(-1* time_difference/10) / (cpt+1))
				else:
					parent_dic[item['directory']][item["author"]]["file_count"] = 0
				if "relative_added" in item:
					parent_dic[item['directory']][item["author"]]["relative_added"] = (item["relative_added"] * 2**(-1* time_difference/10))
				else:
					parent_dic[item['directory']][item["author"]]["relative_added"] = 0
				if "relative_deleted" in item:
					parent_dic[item['directory']][item["author"]]["relative_deleted"] = (item["relative_deleted"] * 2**(-1* time_difference/10))
				else:
					parent_dic[item['directory']][item["author"]]["relative_deleted"] = 0
				parent_dic[item['directory']][item["author"]]["commit_count"]=1
				parent_dic[item['directory']][item['author']]['commit_size'] = []
				if "added_content" in item:
					if "deleted_content" in item:
						parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content']) + len(item['deleted_content'])* 2**(-1* time_difference/10))
					else:
						parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content'])* 2**(-1* time_difference/10))
				else:
					if "deleted_content" in item:
						parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['deleted_content'])* 2**(-1* time_difference/10))
					else:
						parent_dic[item['directory']][item['author']]['commit_size'].append(0)

		else:
			parent_dic[item['directory']] = {}
			parent_dic[item['directory']][item['author']] = {}
			if "files_length" in item:
				parent_dic[item['directory']][item["author"]]["files_length"] = (item["files_length"] * 2**(-1* time_difference/10))
			else:
				parent_dic[item['directory']][item["author"]]["files_length"] = 0
			if "file_count" in item:
				parent_dic[item['directory']][item["author"]]["file_count"] = (item["file_count"] * 2**(-1* time_difference/10) / (cpt+1))
			else:
				parent_dic[item['directory']][item["author"]]["file_count"] = 0
			if "relative_added" in item:
				parent_dic[item['directory']][item["author"]]["relative_added"] = (item["relative_added"] * 2**(-1* time_difference/10))
			else:
				parent_dic[item['directory']][item["author"]]["relative_added"] = 0
			if "relative_deleted" in item:
				parent_dic[item['directory']][item["author"]]["relative_deleted"] = (item["relative_deleted"] * 2**(-1* time_difference/10))
			else:
				parent_dic[item['directory']][item["author"]]["relative_deleted"] = 0
			parent_dic[item['directory']][item["author"]]["commit_count"]=1
			parent_dic[item['directory']][item['author']]['commit_size'] = []
			if "added_content" in item:
				if "deleted_content" in item:
					parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content']) + len(item['deleted_content'])* 2**(-1* time_difference/10))
				else:
					parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['added_content'])* 2**(-1* time_difference/10))
			else:
				if "deleted_content" in item:
					parent_dic[item['directory']][item['author']]['commit_size'].append(len(item['deleted_content'])* 2**(-1* time_difference/10))
				else:
					parent_dic[item['directory']][item['author']]['commit_size'].append(0)


	user_directory_relative = {}

	for item in parent_dic:
		for user in parent_dic[item]:
			if user not in user_directory_relative:
				user_directory_relative[user] = {}
			user_directory_relative[user][item] = statistics.median(parent_dic[item][user]["commit_size"])

	for item in parent_dic:
		for user in parent_dic[item]:
			parent_dic[item][user]["relative_directory_contr"] = user_directory_relative[user][item]/(sum(list(user_directory_relative[user].values()))+1)

	for item in parent_dic:
		for user in parent_dic[item]:
			del parent_dic[item][user]["commit_size"]


	if run_arg == 'trainer':
		with open('final_dir_data', 'w') as outfile:
		    json.dump(parent_dic, outfile)
	else:
		with open('new_commit_data', 'w') as outfile:
		    json.dump(parent_dic, outfile)
