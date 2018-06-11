from __future__ import print_function
from __future__ import division

from glob import glob
import json
import numpy as np
import os
import sys

num_reps = 3
vc_range = [1] + range(6, 35, 6) + [32]
thread_range = [8, 16, 32, 64]

def get_tps_rt_wt(files):
	tps = []
	rt = []
	wt = []
	mc_wait = []
	q_len = []
	for i in range(0, len(files), 2):
		info_dict1 = json.load(open(files[i]))
		info_dict2 = json.load(open(files[i+1]))
		tps.append(info_dict1["tps"] + info_dict2["tps"])
		rt.append((info_dict1["r_time"] + info_dict2["r_time"])/ 2e6)
		wt.append((info_dict1["quing_time"] + info_dict2["quing_time"])/ 2e6)
		mc_wait.append((info_dict1["mc_wait_time"] + info_dict2["mc_wait_time"])/ 2e6)
		q_len.append((info_dict1["avg_q_len"] + info_dict2["avg_q_len"])/ 2)

	return np.mean(tps), np.std(tps), np.mean(rt), np.std(rt), np.mean(wt), np.std(wt), np.mean(mc_wait), np.std(mc_wait), np.mean(q_len), np.std(q_len), tps

if __name__ == "__main__":
	try:
		os.makedirs("csvs")
	except OSError:
		pass
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)

	for num_threads in thread_range:
		f_tps     = open("csvs/write_tps_t_{}_tps.csv".format(num_threads), "w")
		f_rt      = open("csvs/write_tps_t_{}_rt.csv".format(num_threads), "w")
		f_wt      = open("csvs/write_tps_t_{}_q_wt.csv".format(num_threads), "w")
		f_mc_wait = open("csvs/write_tps_t_{}_mc_wait.csv".format(num_threads), "w")
		f_q_len   =  open("csvs/write_tps_t_{}_q_len.csv".format(num_threads), "w")



		for num_vc in vc_range: # set-tps_c-6_t-64_rep-3_mw-2.json
			files = glob("{}/set-tps_c-{}_t-{}*".format(log_dir, num_vc, num_threads))
			files = [file for file in files if file.endswith(".json")]
			assert len(files) == 2*num_reps, "{}/set-tps_c-{}_t-{}*".format(log_dir, num_vc, num_threads)
			tps_mean, tps_stddev, rt_mean, rt_stddev, wt_mean, wt_stddev, mc_wait_mean, mc_wait_stddev, q_len_mean, q_len_stddev, tps = get_tps_rt_wt(files)
			tps = ",".join([str(x) for x in tps])

			f_tps.write("{},{},{},{}\n".format(2*3*num_vc, tps_mean, tps_stddev, tps))
			f_rt.write("{},{},{}\n".format(2*3*num_vc, rt_mean, rt_stddev))
			f_wt.write("{},{},{}\n".format(2*3*num_vc, wt_mean, wt_stddev))
			f_mc_wait.write("{},{},{}\n".format(2*3*num_vc, mc_wait_mean, mc_wait_stddev))
			f_q_len.write("{},{},{}\n".format(2*3*num_vc, q_len_mean, q_len_stddev))

		f_tps.close()
		f_rt.close()
		f_wt.close()
		f_mc_wait.close()
		f_q_len.close()