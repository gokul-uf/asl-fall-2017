from __future__ import print_function
from __future__ import division

from glob import glob
import json
import numpy as np
import os
import sys


num_reps = 3

def get_tps_rt_wt(files):
	tps = []
	rt = []
	wt = []
	for file in files:
		info_dict = json.load(open(file))
		tps.append(info_dict["tps"])
		rt.append(info_dict["r_time"]/ 1e6)
		wt.append(info_dict["quing_time"]/ 1e6)
	return np.mean(tps), np.std(tps), np.mean(rt), np.std(rt), np.mean(wt), np.std(wt), tps

if __name__ == "__main__":
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)

	try:
		os.makedirs("csvs")
	except OSError:
		pass

	modes = ["r-o", "w-o"]
	client_range = [2, 4, 8, 16, 32, 64, 128]
	thread_range = [8, 16, 32, 64]
	for mode in modes:
		for num_threads in thread_range:
			f_tps = open("csvs/one_mw_baseline_{}_t_{}_tps.csv".format(mode, num_threads), "w")
			f_rt  = open("csvs/one_mw_baseline_{}_t_{}_rt.csv".format(mode,  num_threads), "w")
			f_wt  = open("csvs/one_mw_baseline_{}_t_{}_wt.csv".format(mode,  num_threads), "w")

			for num_vc in client_range: # one-mw_r-o_c-18_t-64_rep-2.json
				files = glob("{}/one-mw_{}_c-{}_t-{}_*".format(log_dir, mode, num_vc, num_threads))
				files = [file for file in files if file.endswith(".json")]
				files.sort()
				assert len(files) == num_reps, (len(files), num_reps, "{}/one-mw_{}_c-{}_t-{}_*".format(log_dir, mode, num_vc, num_threads))
				tps_mean, tps_stddev, rt_mean, rt_stddev, wt_mean, wt_stddev, tps = get_tps_rt_wt(files)
				tps = ",".join([str(x) for x in tps])

				f_tps.write("{},{},{},{}\n".format(2*num_vc, tps_mean, tps_stddev, tps))
				f_rt.write("{},{},{}\n".format(2*num_vc, rt_mean, rt_stddev))
				f_wt.write("{},{},{}\n".format(2*num_vc, wt_mean, wt_stddev))
			f_tps.close()
			f_rt.close()
			f_wt.close()