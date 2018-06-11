from __future__ import print_function
from __future__ import division

import json
import numpy as np
import os
from pprint import pprint
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

def get_closest(js_file, percentile): # get latency upto the closest percentile
	lat_list = js_file["ALL STATS"]["GET"]
	diff = 500
	best_set = lat_list[0]
	for lat_set in lat_list:
		if(abs(lat_set['percent'] - percentile) < diff):
			best_set = lat_set
			diff = abs(lat_set['percent'] - percentile)
	return best_set['<=msec']

def combine_rep_files(files):
	assert len(files) == num_mw * num_mc
	p_map = {p:[] for p in percentiles}
	for file in files:
		js = json.load(open(file))
		for percentile in percentiles:
			p = get_closest(js, percentile)
			p_map[percentile].append(p)

	p_map = {x:np.mean(p_map[x]) for x in p_map}
	return p_map

def combine_key_rep_files(rep_files, percentile):
	lat_list = []
	for file in rep_files:
		js = json.load(open(file))
		l = get_closest(js, percentile)
		lat_list.append(l)
	return np.mean(lat_list)

def plot_mt_percentile_group_by_key(shard_mode, num_keys, log_dir ,start_idx): # from clients
	prefix = "mt_s-{}_g-{}*".format(shard_mode, num_keys)  # all files for a given shard mode and number of keys
	pattern = os.path.join(log_dir, prefix)
	files = glob(pattern)
	assert len(files) == num_reps * num_mw * num_mc, (num_reps * num_mw * num_mc, len(files), pattern) # num_reps*2 middleware * 3 clients
	files.sort()

	vals = []
	err = []
	dicts = {p:[] for p in percentiles}

	for i in range(0, len(files), 6):
		dc = combine_rep_files(files[i: i+6])
		for key in dc:
			dicts[key].append(dc[key])
	for percentile  in percentiles:
		vals.append(np.mean(dicts[percentile]))
		err.append(  np.std(dicts[percentile]))

	plt.bar(left = range(start_idx, start_idx + len(percentiles)),
			height = vals, yerr = err, capsize = 2, label = "{} Keys".format(num_keys))
	return dicts

def plot_mt_percentile_group_by_percentile(shard_mode, log_dir, percentile, start_idx): # plot bars for each percentile, group by num-keys
	files = glob(log_dir + "/*mt_s-{}*".format(shard_mode))
	files = [f for f in files if f.endswith("json")]
	files.sort()

	vals = []
	err  = []

	dicts = {k:[] for k in multi_get_keys}

	for key in multi_get_keys: # files with only one count of GET keys
		key_files = [file for file in files if "g-{}".format(key) in file]
		assert len(key_files) == num_mw * num_mc, len(key_files)
		for i in range(num_reps):
			rep_files = [f for f in key_files if "rep-{}".format(i) in f]
			dc = combine_key_rep_files(rep_files, percentile)


		pprint(key_files)
		exit(0)


if __name__ == "__main__":
	log_dir = sys.argv[1]
	log_dir = os.path.abspath(log_dir)
	
	for shard_mode in shard_modes:
		print("plotting MT percentiles, grouped by multi-GET keys, shard: {}".format(shard_mode))
		percentile_dict = {} 
		plt.figure()
		plt.title("Response Time Percentiles from MT Grouped by multi-GET Keys (Sharding: {})".format(shard_mode), fontsize = 10.5)

		for i, num_keys in enumerate(multi_get_keys):
			dc = plot_mt_percentile_group_by_key(shard_mode, num_keys, log_dir, start_idx =  1 + i*len(percentiles))
			percentile_dict[num_keys] = dc

		plt.legend()
		plt.xlim(xmin = 0)
		plt.ylim(ymin = 0)
		plt.ylabel("Response Time (msec)")
		plt.xlabel("Percentiles")
		plt.xticks(range(1, 21), percentiles * len(multi_get_keys))	
		plt.savefig("5_shard_{}_percentiles_group_by_keys_mt.png".format(shard_mode))


		print("plotting MT percentiles, grouped by percentiles, shard: {}".format(shard_mode))
		plt.figure()
		plt.title("Response Time Percentiles from MT Grouped by percentiles (Sharding: {})".format(shard_mode), fontsize = 10.5)

		for start_idx, percentile in enumerate(percentiles):
			vals = []
			err  = []
			for num_keys in multi_get_keys:
				val_arr = percentile_dict[num_keys][percentile]
				vals.append(np.mean(val_arr))
				err.append( np.std(val_arr))
			plt.bar(left = range(1 + start_idx*len(multi_get_keys), 1 + (start_idx + 1)*len(multi_get_keys)),
			height = vals, yerr = err, capsize = 2, label = "{}-th percentile".format(percentile))


		plt.legend()
		plt.xlim(xmin = 0)
		plt.ylim(ymin = 0)
		plt.ylabel("Response Time (msec)")
		plt.xlabel("Num multi-GET keys")
		plt.xticks(range(1, 21), multi_get_keys * len(percentiles))	
		plt.savefig("5_shard_{}_percentiles_group_by_percentile_mt.png".format(shard_mode))