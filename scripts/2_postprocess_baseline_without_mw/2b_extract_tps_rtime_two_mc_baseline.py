from __future__ import print_function

import os
import sys
from glob import glob
import json
import numpy as np

def get_tps_rt(files, mode):
	rep_tps = []
	rep_rt = []
	for i in range(0, 3):
		rep_files = [files[i], files[i+3]] # mc_1_rep_i, mc_2_rep_i
		tps, rt = combine_rep_files(rep_files, mode)
		rep_tps.append(tps)
		rep_rt.append(rt)

	assert len(rep_tps) == 3
	assert len(rep_rt)  == 3
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
	# client_range = [1] + range(5, 155, 10)
	client_range = range(5, 155, 10)
	modes = ["r-o", "w-o"]

	for mode in modes:
		f_tps = open("csvs/two_mc_baseline_{}_tps.csv".format(mode), "w")
		f_rt  = open("csvs/two_mc_baseline_{}_rt.csv".format(mode), "w")

		for num_vc in client_range:
			files = glob("{}/mt_{}_c-{}_*".format(log_dir, mode, num_vc))
			files.sort()
			assert len(files) == 6, len(files)  # 3 reps, 2 MT Instances

			tps_mean, tps_stddev, rt_mean, rt_std, tps, rt = get_tps_rt(files, mode)
			rt  = ','.join([str(x) for x in rt])
			tps = ','.join([str(x) for x in tps])
			f_tps.write("{},{},{},{}\n".format(2*num_vc, tps_mean, tps_stddev, tps))
			f_rt.write("{},{},{},{}\n".format(2*num_vc, rt_mean, rt_std, rt))
		f_tps.close()
		f_rt.close()