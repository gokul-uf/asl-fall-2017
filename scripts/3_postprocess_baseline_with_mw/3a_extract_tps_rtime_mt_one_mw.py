from __future__ import print_function

import sys
from glob import glob
import json
import numpy as np
import os

modes = ["r-o", "w-o"]
num_reps = 3
client_range = [2, 4, 8, 16, 32, 64, 128]
thread_range = [8, 16, 32, 64]

def get_tps_std(files, mode):
	tps = []
	rt  = []

	if mode == "r-o":
		cmd = "Gets"
	else:
		cmd = "Sets"

	for file in files:
		js = json.load(open(file))
		assert js["ALL STATS"][cmd]["Misses/sec"] == 0.0, file
		tps.append(js["ALL STATS"][cmd]["Ops/sec"])
		rt.append(js["ALL STATS"][cmd]["Latency"])

	return np.mean(tps), np.std(tps), np.mean(rt), np.std(rt)

if __name__ == "__main__":
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)

	try:
		os.makedirs("csvs")
	except OSError:
		pass

	for mode in modes:
		for num_threads in thread_range:
			f_tps = open("csvs/one_mw_baseline_mt_{}_t_{}_tps.csv".format(mode, num_threads), "w")
			f_rt  = open("csvs/one_mw_baseline_mt_{}_t_{}_rt.csv".format(mode,  num_threads), "w")
			
			for num_vc in client_range:
				files = glob("{}/mt_{}_c-{}_t-{}_*".format(log_dir, mode, num_vc, num_threads))
				assert len(files) == num_reps, "{}/mt_{}_c-{}_t-{}_*".format(log_dir, mode, num_vc, num_threads)
				
				tps_mean, tps_std, rt_mean, rt_std = get_tps_std(files, mode)			
				
				f_tps.write("{},{},{}\n".format(2*num_vc, tps_mean, tps_std))
				f_rt.write("{},{},{}\n".format(2*num_vc,   rt_mean,  rt_std))

			f_tps.close()
			f_rt.close()