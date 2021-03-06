import csv
from collections import defaultdict
import operator
import json
from datetime import datetime
import os
import math
from db_conn import db
from flask import session
def diff(t1 , t2):
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp1 = datetime.strptime(str(t1), fmt)
	tstamp2 = datetime.strptime(str(t2), fmt)
	p = tstamp2 - tstamp1
	return p.total_seconds()
def convert(t):
	t = int(t)
	hour = t//3600
	t%=3600
	mint = t//60
	t%=60
	sec = t
	return str(hour)+":"+str(mint)+":"+str(sec)

def ranking(contest_code , problems_list , original_start_time , start_time , current_time , is_friends):

	contest_code = contest_code.upper()
	username = session['username']
	user_data = db['user_data'].find({'_id':username})
	user_data = user_data[0]
	friend_list = user_data['friends']
	friends = []
	for friend in friend_list:
		friends.append(friend[0])
	# link = str(os.getcwd())+'/COOKOFF-dataset/' + contest_code + '.csv'
	collections = db[contest_code]
	ranklist = []
	current_rank_list = []
	total_names = set()
	total_names.add('*' + username)
	for row in collections.find():
			total_names.add(row["username"])
	for name in total_names:
		user = {}
		user['rank'] = 0
		user['name'] = name
		user['entry'] = False
		user['Total Score'] = 0
		user['Penalty'] = 0
		user['Total'] = 0
		for problem in problems_list:
			user[problem] = 0
			user[problem+"Time"] = 0
		ranklist.append(user)
	for row in collections.find().sort('id'):
		time_diff1 = diff(start_time , current_time)
		time_diff2 = diff(original_start_time , row["date"])
		if time_diff2 > time_diff1:
			continue
		name = row["username"]
		for i in range(0,len(ranklist)):
			if ranklist[i]['name'] == name:
				ranklist[i]['entry'] = True
				if row["result"] == "AC" and ranklist[i][row["problemCode"]] <= 0:
					ranklist[i][row["problemCode"]] = 1 + (ranklist[i][row["problemCode"]] * (-1))
					ranklist[i][row["problemCode"]+"Time"] = time_diff2
				elif ranklist[i][row["problemCode"]]<=0:
					ranklist[i][row["problemCode"]]-=1
				ranklist[i]['Total Score'] = 0
				ranklist[i]['Penalty'] = 0
				ranklist[i]['Total'] = 0
				for problem in problems_list:
					if ranklist[i][problem] > 0:
						ranklist[i]['Total Score']+=1
						ranklist[i]['Penalty']+=ranklist[i][problem+"Time"]
						ranklist[i]['Penalty']+=(ranklist[i][problem]-1)*1200
						ranklist[i]['Total']+=100000000									
				ranklist[i]['Total']-=ranklist[i]['Penalty']
				ranklist[i]['Penalty'] = convert(ranklist[i]['Penalty'])
				break
	prev_score = -1
	cnt = 0
	ranklist.sort(key=operator.itemgetter('Total') , reverse = True)
	for val in ranklist:
		if val['entry'] == True:
			if is_friends:
				virtual_name = val['name']
				if val['name'][0] == '*':
					virtual_name = val['name'][1:]
				if virtual_name in friends or virtual_name == username:
					if val['Total']!=prev_score:
						cnt+=1
						val['rank'] = cnt
					else:
						val['rank'] = cnt
					prev_score = val['Total']
					current_rank_list.append(val)
				else:
					continue
			else:
				if val['Total']!=prev_score:
					cnt+=1
					val['rank'] = cnt
				else:
					val['rank'] = cnt
				prev_score = val['Total']
				current_rank_list.append(val)
	for val in current_rank_list:
		for problem in problems_list:
			val[problem+"Time"] = convert(val[problem+"Time"])
	return current_rank_list


def dashboard(contest_code , problems_list, original_start_time , start_time , current_time):

	contest_code = contest_code.upper()
	# link = str(os.getcwd())+'/COOKOFF-dataset/' + contest_code + '.csv'
	collections = db[contest_code]
	submission = []
	user_submissions = []
	total_names = set()
	for row in collections.find():
			total_names.add(row["username"])
	for name in total_names:
		user = {}
		user['name'] = name
		for problem in problems_list:
			user[problem] = 0
		user_submissions.append(user)
	for val in problems_list:
		p = {}
		p['problem_name'] = val
		p['correct'] = 0
		p['total'] = 0
		p['accuracy'] = 0
		submission.append(p)
	for row in collections.find().sort('id'):
		time_diff1 = diff(start_time , current_time)
		time_diff2 = diff(original_start_time , row["date"])
		if time_diff2 > time_diff1:
			continue
		name = row["username"]
		for i in range(0,len(user_submissions)):
			if user_submissions[i]['name'] == name:
				if row["result"] == "AC" and user_submissions[i][row["problemCode"]] <= 0:
					user_submissions[i][row["problemCode"]] = 1 + (user_submissions[i][row["problemCode"]] * (-1))
				elif user_submissions[i][row["problemCode"]]<=0:
					user_submissions[i][row["problemCode"]]-=1
				break
	for val in user_submissions:
		for i in range(0 , len(problems_list)):
			if val[problems_list[i]]!=0:
				if val[problems_list[i]] > 0:
					submission[i]['correct']+=1
				submission[i]['total']+=abs(val[problems_list[i]])
				submission[i]['accuracy'] = str(round((submission[i]['correct']/submission[i]['total'])*100 , 2))
		# for i in range(0,len(submission)):
		# 	if submission[i]['problem_name'] == row["problemCode"]:
		# 		if row["result"] == 'AC':
		# 			submission[i]['correct']+=1
		# 		submission[i]['total']+=1
		# 		submission[i]['accuracy'] = str(round((submission[i]['correct']/submission[i]['total'])*100 , 2))
	# json_file = json.dumps(submission , indent = 4)
	# print(json_file)
	return submission
# ranking('COOK01' , problems , '2010-07-24 21:30:00' , '2018-09-17 16:40:00' , '2018-09-17 16:53:00')
# dashboard('2018-06-17 21:30:00' , '2018-06-17 21:45:00')
