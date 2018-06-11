from __future__ import print_function
from __future__ import division

import json
import numpy as np
import os
from pprint import pprint
import sys
from glob import glob
import matplotlib.pyplot as plt

shard_modes = [False, True]

num_reps = 3
num_mt = 3
num_mw = 2

def get_bins():
	return {x / 10. : 0 for x in range(0, 100)}

def trunc(num, digits  = 1):
	sp = str(num).split('.')
	sp = '.'.join([sp[0], sp[1][:digits]])
	return float(sp)

def combine_mt_files(mt_files):
	mt_bins = get_bins()

	for mt_file in mt_files:
		mt_bin = get_mt_bins(mt_file)
		for val in mt_bin.keys():
			mt_bins[val] += mt_bin[val]

	return mt_bins

def get_mt_bins(mt_file):
	js = json.load(open(mt_file))
	num_reqs = js["configuration"]["test_time"]*js["ALL STATS"]["Gets"]["Ops/sec"]
	lat_list = js["ALL STATS"]["GET"]

	bins = get_bins()
	prev_percent = 0

	for block in lat_list:
		cur_percent = block["percent"]
		val = block["<=msec"]
		val = trunc(val)
		if val in bins:
			bins[val] = num_reqs * (cur_percent - prev_percent) / 100.0
			prev_percent = cur_percent

	return bins

def combine_rep_bins(rep_bins):
	ret_bin = get_bins()
	# for rep_bin in rep_bins:
	# 	for val in rep_bin.keys():
	# 		ret_bin[val] += rep_bin[val]
	# for val in ret_bin.keys():
	# 	ret_bin[val] /= float(num_reps)
	for val in ret_bin.keys():
		ret_bin[val] = np.mean([r[val] for r in rep_bins])

	return ret_bin

def plot_hist(shard_mode, bins):
	lefts = bins.keys()
	lefts.sort()

	vals = []

	for key in lefts:
		vals.append(bins[key])

	plt.figure()
	plt.title("Histogram of Response Times Measured at client (sharding: {})".format(shard_mode))
	plt.xlabel("Response Time (msec)")
	plt.ylabel("Num Requests")
	plt.bar(lefts, vals)
	plt.xticks(range(11))
	plt.savefig("5_mt_hist_shard_{}.png".format(shard_mode))


if __name__ == "__main__":
	base_log_dir = sys.argv[1]
	base_log_dir = os.path.abspath(base_log_dir)

	for shard_mode in shard_modes:
		rep_bins = [{}] * num_reps

		for rep in range(1, num_reps + 1):
			prefix = "mt_s-{}_g-6_rep-{}*".format(shard_mode, rep)
			mt_files = glob(os.path.join(base_log_dir, prefix))
			assert len(mt_files) == num_mw * num_mt

			rep_bin = combine_mt_files(mt_files)
			rep_bins[rep - 1] = rep_bin

		bins = combine_rep_bins(rep_bins)
		plot_hist(shard_mode, bins) 