from __future__ import print_function
from __future__ import division

import json
import numpy as np
import os
import seaborn as sns
import sys
from glob import glob
import matplotlib.pyplot as plt


multi_get_keys = [1, 3, 6, 9]
shard_modes = [True, False]
percentiles = [25, 50, 75, 90, 99]
num_reps = 3
num_mw = 2
num_mc = 3


def combine_rep_files(rep_files):
	assert len(rep_files) == num_mw * num_mc
	r_times = []
	for file in rep_files:
		js = json.load(open(file))
		assert js["ALL STATS"]["Gets"]["Misses/sec"] == 0, file
		r_times.append(js["ALL STATS"]["Gets"]["Latency"])
	return np.mean(r_times)

def get_val_n_error(shard_mode, num_keys, log_dir):
	prefix = "mt_s-{}_g-{}*".format(shard_mode, num_keys)
	pattern = os.path.join(log_dir, prefix)
	files = glob(pattern)
	assert len(files) == num_reps * num_mw * num_mc, pattern # num_reps*2 middleware * 3 clients
	files.sort()

	r_times = []
	for i in range(0, len(files), 6):
		rep_files = files[i: i+6]
		r_time = combine_rep_files(rep_files)
		r_times.append(r_time)

	return np.mean(r_times), np.std(r_times)


if __name__ == "__main__":
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)
	print("plotting average throughput from MT")
	
	for shard_mode in shard_modes:
		plt.figure()
		plt.title("Average Response Time (from MT) vs Number of Keys (Sharding: {})".format(shard_mode))
		vals = []
		errors = []
		for num_keys in multi_get_keys:
			val, err = get_val_n_error(shard_mode, num_keys, log_dir)
			vals.append(val)
			errors.append(err)
		plt.bar(range(1, 1 + len(multi_get_keys)), vals, yerr = errors, capsize = 2)
		plt.plot(range(1, 1 + len(multi_get_keys)), vals)
		# plt.bar(range(len(multi_get_keys)), vals, yerr = errors, capsize = 2)
		# plt.plot(range(len(multi_get_keys)), vals)
		plt.xlabel("# GET Keys")
		plt.ylabel("Response Time (msec)")
		plt.xticks(range(1, 1 + len(multi_get_keys)), multi_get_keys)
		# plt.xticks(range(len(multi_get_keys)), multi_get_keys)
		plt.ylim(ymin = 0)
		plt.xlim(xmin = 0)
		plt.savefig("5_shard_{}_avg_r_times_mt.png".format(shard_mode))

