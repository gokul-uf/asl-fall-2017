# creates the tables needed for the 2K analysis part

from __future__ import print_function
from __future__ import division

from glob import glob
import os
import json
import numpy as np
import sys

modes = ["r-o", "w-o",  "r-w"]
num_mc = ["2", "3"]
num_mw = ["1", "2"]
num_threads = ["8", "32"]
num_reps = 3
num_mt = 3

def get_code(num):
	ret_val = ""
	num = bin(num)
	num = num[2:]
	num = str(num).zfill(3)

	for val in num:
		assert val in ["1", "0"]
		if val == "0":
			ret_val += "-1,"
		else: 
			ret_val += "1,"

	return ret_val[:-1]

def merge_rep_files(files):
	js1 = json.load(open(files[0]))
	js2 = json.load(open(files[1]))
	tps = js1["tps"] + js2["tps"]
	lat = np.mean([js1["r_time"], js2["r_time"]])

	return tps, lat

def get_ops(mode):
	if mode == "r-o":
		return ["Gets"]
	elif mode == "w-o":
		return ["Sets"]
	else:
		return ["Gets", "Sets"]

def get_tps_lat(files, mw_count, mode):
	# combine tps and lat across all 3 clients and 2 MW (if there are)
	tps_list = []
	lat_list = []

	assert mode in modes
	assert len(files) == mw_count*num_mt, (mw_count, num_mt, len(files), files)
	ops = get_ops(mode)

	for file in files:
		js = json.load(open(file))
		# for op in ops:
		tps_list.append(js["ALL STATS"]["Totals"]["Ops/sec"])
		lat_list.append(js["ALL STATS"]["Totals"]["Latency"])

	tps =  np.sum(tps_list)
	lat = np.mean(lat_list)
	return tps, lat

if __name__ == "__main__": # mt_r-o_mc-2_mw-1_t-8-rep-1_mw-1.json
	log_dir = os.path.abspath(sys.argv[1])
	# print("WARN: Using old prefix style with '-' inbetween t and rep, change when you have new logs")
	js_files = glob("{}/*.json".format(log_dir))
	if len(js_files) == 0:
		print("ERROR: Found no JSON files, please give the directory of the MT logs")
	for mode in modes:
		print("creating tables for mode: {}".format(mode))
		f_tps = open("{}_tps.csv".format(mode), "w")
		f_lat = open("{}_lat.csv".format(mode), "w")

		f_tps.write("MC,MW,Threads,TPS_1,TPS_2,TPS_3\n")
		f_lat.write("MC,MW,Threads,LAT_1,LAT_2,LAT_3\n")
		
		count = 0
		for mc_count in num_mc:
			for mw_count in num_mw:
				for thread_count in num_threads:
					tps_list = []
					lat_list = []
					for rep in range(1, num_reps + 1):

						prefix = "mt_{}_mc-{}_mw-{}_t-{}_rep-{}*".format(mode, mc_count, mw_count, thread_count, rep)
					
						files = glob("{}/{}".format(log_dir, prefix))
						files.sort()
						assert len(files) == int(mw_count)*num_mt, (len(files), mw_count)

						t, l = get_tps_lat(files, int(mw_count), mode)
						tps_list.append(str(t))
						lat_list.append(str(l))
					
					tps_list = ",".join(tps_list)
					lat_list = ",".join(lat_list)
					
					idx = get_code(count)
					f_tps.write(idx + "," + tps_list + "\n")
					f_lat.write(idx + "," + lat_list + "\n")
					count += 1

		f_tps.close()
		f_lat.close()
