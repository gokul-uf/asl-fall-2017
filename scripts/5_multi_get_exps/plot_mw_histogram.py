from __future__ import print_function
from __future__ import division

from glob import glob
import numpy as np
import os
import matplotlib.pyplot as plt
import sys

# only for 6 keys, Multi-GET
shard_modes = [False, True]

num_mw = 2
num_reps = 3

num_bins = 1200
bin_width = 0.1  # milliseconds

bar_width = 0.1
bin_min = 0
bin_max = 120

def get_bins():
	bins = {x  / 10 :0 for x in range(bin_min, bin_max * 10)}
	assert len(bins) == num_bins, len(bins)
	return bins

def trunc(num, digits):
	sp = str(num).split('.')
	sp = '.'.join([sp[0], sp[1][:digits]])
	return float(sp)

def get_r_time(line):
	line = line.strip().split()[1:]
	line = [float(x) for x in line]
	r_time = abs(line[8] - line[0]) / 1e6

	# round to nearest .1
	r_time = trunc(r_time, 1)
	return r_time

def get_mw_bins(folder):
	info_files = glob(os.path.join(folder, "*.info"))
	info_files = [f for f in info_files if "id" in f]
	bins = get_bins()
	
	# print("processing {} info files".format(len(info_files)))
	for info_file in info_files:
		with open(info_file) as f:
			for line in f:
				if line.startswith("g"):
					r_time = get_r_time(line)
					bins[r_time] += 1

	return bins

def combine_mw_files(mw_files):
	# print("combining Response Times across Middlewares")
	mw_bins_1 = get_mw_bins(mw_files[0])
	mw_bins_2 = get_mw_bins(mw_files[1])
	bins = get_bins()

	for val in bins.keys():
		bins[val] += mw_bins_1[val]
		bins[val] += mw_bins_2[val]

	return bins

def combine_rep_bins(rep_bins):
	# print("combining Response Times across reps")
	mean_bins = get_bins()
	std_bins  = get_bins()

	for val in mean_bins.keys():
		mean_bins[val] = np.mean([r[val] for r in rep_bins])
		std_bins[val]  = np.std( [r[val] for r in rep_bins])

	return mean_bins, std_bins

def plot_hist(mean_bin, std_bin, shard_mode):
	# print("plotting histogram")
	vals = mean_bin.keys()
	vals.sort()
	means = []
	stds = []

	for val in vals:
		means.append(mean_bin[val])
		stds.append(std_bin[val])

	means = np.asarray(means)
	stds = np.asarray(stds)
	means /= 4.
	stds /= 4.

	plt.figure()
	plt.xlabel("Response Time (msec)")
	plt.ylabel("Num Requests")

	plt.title("Distribution of Response Times at MW, Sharding: {}".format(shard_mode))
	plt.bar(left = vals, height = means)
	plt.savefig("5_mw_hist_shard_{}.png".format(shard_mode))

	plt.figure()
	plt.xlabel("Response Time (msec)")
	plt.ylabel("log(Num Requests)")

	plt.title("Distribution of log(Response Times) at MW, Sharding: {}".format(shard_mode))
	h = []
	for x in means:
		if x < 1:
			x *= 4.
		h.append(x)
	heights = np.asarray(h)

	np.seterr(divide='ignore')
	heights = np.log10(means)
	np.seterr(divide='warn')
	heights[np.isneginf(heights)] = 0


	plt.ylim(ymin = np.min(heights), ymax = np.max(heights) + 2)
	
	plt.yticks(np.arange(np.min(heights),np.max(heights) + 2, 0.5 ))
	
	plt.bar(left = vals, height = heights)
	plt.axhline(color = "black")
	plt.savefig("5_mw_log_hist_shard_{}.png".format(shard_mode))

if __name__ == "__main__":
	base_log_dir = sys.argv[1]
	base_log_dir = os.path.abspath(base_log_dir)

	for shard_mode in shard_modes:
		rep_bins = [{}] * num_reps
		assert len(rep_bins) == num_reps, len(rep_bins)

		for rep in range(1, num_reps + 1): # gets-exp_s-True_g-6_rep-1_mw-1_log
			prefix = "gets-exp_s-{}_g-6_rep-{}*".format(shard_mode, rep)
			prefix = os.path.join(base_log_dir, prefix)

			mw_files = glob(prefix)
			assert len(mw_files) == num_mw, len(mw_files)

			rep_bin = combine_mw_files(mw_files)
			rep_bins[rep - 1] = rep_bin

		# print("combining rep bins")
		mean_bin, std_bin = combine_rep_bins(rep_bins)

		print("plotting shard: {}".format(shard_mode))
		plot_hist(mean_bin, std_bin, shard_mode)
