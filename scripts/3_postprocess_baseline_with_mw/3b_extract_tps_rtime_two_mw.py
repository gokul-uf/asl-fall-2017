from __future__ import print_function
from __future__ import division

from glob import glob
import json
import numpy as np
import os
import sys

num_reps = 3

# plot tps and rt measured at MW

def get_tps_rt_wt(files):
	rep_tps = []
	rep_rt = []
	rep_wt = []
	rep_nt_time = []
	rep_wt_time = []
	rep_q_len   = []

	for i in range(num_reps):
		rep_files = [files[i], files[i + num_reps]]
		tps, rt, wt, nt, wtt, q_len = combine_rep_files(rep_files)

		rep_tps.append(tps)
		rep_rt.append(rt / 1e6)
		rep_wt.append(wt / 1e6)
		rep_nt_time.append(nt / 1e6)
		rep_wt_time.append(wtt / 1e6)
		rep_q_len.append(q_len)

	assert len(rep_tps) == num_reps
	assert len(rep_rt) == num_reps
	assert len(rep_wt) == num_reps
	return (np.mean(rep_tps), np.std(rep_tps), 
			np.mean(rep_rt), np.std(rep_rt), 
			np.mean(rep_wt), np.std(rep_wt), rep_tps,
			np.mean(rep_nt_time), np.std(rep_nt_time),
			np.mean(rep_wt_time), np.std(rep_wt_time),
			np.mean(rep_q_len),   np.std(rep_q_len)
			)

def combine_rep_files(files):
	tps   = []
	rt    = []
	wt    = []
	nt    = []
	wtt   = []
	q_len = []

	for file in files:
		js = json.load(open(file))
		tps.append(js["tps"])
		rt.append(js["r_time"])
		wt.append(js["quing_time"])
		nt.append(js["nt_service_time"])
		wtt.append(js["wt_postprocess_time"])
		q_len.append(js["avg_q_len"])

	return (np.sum(tps), np.mean(rt), np.mean(wt), 
			np.mean(nt), np.mean(wtt), np.mean(q_len))


if __name__ == "__main__":
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)
	
	modes = ["r-o", "w-o"]
	client_range = [2, 4, 8, 16, 32, 64, 128]
	thread_range = [8, 16, 32, 64]

	for mode in modes:
		for num_threads in thread_range:
			f_tps   = open("csvs/two_mw_baseline_{}_t_{}_tps.csv".format(mode, num_threads), "w")
			f_rt    = open("csvs/two_mw_baseline_{}_t_{}_rt.csv".format(mode,  num_threads), "w")
			f_wt    = open("csvs/two_mw_baseline_{}_t_{}_wt.csv".format(mode,  num_threads), "w")
			f_nt    = open("csvs/two_mw_baseline_{}_t_{}_nt.csv".format(mode,  num_threads), "w")
			f_wtt   = open("csvs/two_mw_baseline_{}_t_{}_wtt.csv".format(mode,  num_threads), "w")
			f_q_len = open("csvs/two_mw_baseline_{}_t_{}_qlen.csv".format(mode,  num_threads), "w")
			for num_vc in client_range:
				files = glob("{}/two-mw_{}_c-{}_t-{}*".format(log_dir, mode, num_vc, num_threads))
				files = [file for file in files if file.endswith(".json")]
				files.sort()
				assert len(files) == 2*num_reps, (len(files), "{}/two-mw_{}_c-{}_t-{}*".format(log_dir, mode, num_vc, num_threads)) # one for each MW
				tps_mean, tps_stddev, rt_mean, rt_stddev, wt_mean, wt_stddev, tps, nt_mean, nt_std, wtt_mean, wtt_std, q_len_mean, q_len_std = get_tps_rt_wt(files)
				tps = ",".join([str(x) for x in tps])

				f_tps.write("{},{},{},{}\n".format(2*num_vc, tps_mean, tps_stddev, tps))
				f_rt.write("{},{},{}\n".format(2*num_vc, rt_mean, rt_stddev))
				f_wt.write("{},{},{}\n".format(2*num_vc, wt_mean, wt_stddev))
				f_nt.write("{},{},{}\n".format(2*num_vc, nt_mean, nt_std))
				f_wtt.write("{},{},{}\n".format(2*num_vc, wtt_mean, wtt_std))
				f_q_len.write("{},{},{}\n".format(2*num_vc, q_len_mean, q_len_std))

			f_tps.close()
			f_rt.close()
			f_wt.close()
			f_nt.close()
			f_wtt.close()
			f_q_len.close()