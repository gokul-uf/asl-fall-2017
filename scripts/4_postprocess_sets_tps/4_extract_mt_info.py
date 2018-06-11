from __future__ import print_function

import sys
from glob import glob
import json
import numpy as np
import os

num_reps = 3
num_mt = 3
num_mw = 2

client_range = [1, 6, 12, 18, 24, 30, 32]
thread_range = [8, 16, 32, 64]

def get_tps_rt(files):
	files.sort()
	rep_tps = []
	rep_rt  = []
	for i in range(0, len(files), 6):
		rep_files = files[i:i+6]
		tps, rt = combine_rep_files(rep_files)
		rep_tps.append(tps)
		rep_rt.append(rt)
	return np.mean(rep_tps), np.std(rep_tps), np.mean(rep_rt), np.std(rep_rt)

def combine_rep_files(files):
	tps = []
	rt  =  []

	for file in files:
		js = json.load(open(file))
		tps.append(js["ALL STATS"]["Sets"]["Ops/sec"])
		rt.append(js["ALL STATS"]["Sets"]["Latency"])
	return np.sum(tps), np.mean(rt)


if __name__ == "__main__":
	try:
		os.makedirs("csvs")
	except OSError:
		pass
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)

	for num_thread in thread_range:
		f_tps = open("csvs/set_tps_t-{}_mt_tps.csv".format(num_thread), "w")
		f_rt = open("csvs/set_tps_t-{}_mt_rt.csv".format(num_thread), "w")

		for num_vc in client_range:
			files = glob("{}/mt_c-{}_t-{}*".format(log_dir, num_vc, num_thread))
			assert len(files)  == num_reps * num_mt * num_mw, files
			files.sort()

			tps_mean, tps_stddev, rt_mean, rt_std = get_tps_rt(files)

			f_tps.write("{},{},{}\n".format(3*2*num_vc, tps_mean, tps_stddev))
			f_rt.write("{},{},{}\n".format(3*2*num_vc, rt_mean, rt_std))

		f_tps.close()
		f_rt.close()	