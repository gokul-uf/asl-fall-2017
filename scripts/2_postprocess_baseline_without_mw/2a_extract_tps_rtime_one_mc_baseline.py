from __future__ import print_function

import sys
from glob import glob
import json
import numpy as np
import os

def get_tps_rt(files, mode):
	rep_tps = []
	rep_rt = []
	for i in range(0, len(files), 3):
		rep_files = files[i:i+3]
		tps, rt = combine_rep_files(rep_files, mode)
		rep_tps.append(tps)
		rep_rt.append(rt)

	return np.mean(rep_tps), np.std(rep_tps), np.mean(rep_rt), np.std(rep_rt), rep_tps, rep_rt

def combine_rep_files(files, mode):
	tps = []
	rt = []

	if mode == "r-o":
		cmd = "Gets"
	else:
		cmd = "Sets"

	for file in files:
		js = json.load(open(file))
		assert js["ALL STATS"][cmd]["Misses/sec"] == 0.0, file
		tps.append(js["ALL STATS"][cmd]["Ops/sec"])
		rt.append(js["ALL STATS"][cmd]["Latency"])

	return np.sum(tps), np.mean(rt)

if __name__ == "__main__":
	try:
		os.makedirs("csvs")
	except OSError:
		pass
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)
	# client_range = [1] + range(5, 155, 10)
	client_range = range(5, 155, 10)
	modes = ["r-o", "w-o"]



	for mode in modes:
		f_tps = open("csvs/one_mc_baseline_{}_tps.csv".format(mode), "w")
		f_rt  = open("csvs/one_mc_baseline_{}_rt.csv".format(mode), "w")

		for num_vc in client_range:
			files = glob("{}/mt_{}_c-{}_*".format(log_dir, mode, num_vc))
			files.sort()
			# print(files)
			assert len(files) == 9, files  # 3 reps, 3 MT VMs

			tps_mean, tps_stddev, rt_mean, rt_std, tps, rt = get_tps_rt(files, mode)
			rt  = ','.join([str(x) for x in rt])
			tps = ','.join([str(x) for x in tps])
			f_tps.write("{},{},{},{}\n".format(3*2*num_vc, tps_mean, tps_stddev, tps))
			f_rt.write("{},{},{},{}\n".format(3*2*num_vc, rt_mean, rt_std, rt))
		f_tps.close()
		f_rt.close()