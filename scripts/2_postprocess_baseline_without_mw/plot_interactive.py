from __future__ import print_function
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

modes = ["r-o", "w-o"]

def get_vals(file):
	lines = file.read().split("\n")[:-1]
	lines = [line.strip().split(',') for line in lines]
	vals = [float(line[1]) for line in lines]
	return vals

if __name__ == "__main__":
	plt.figure()
	plt.title("Interactive Law for One MC Experiments")

	for mode in modes:
		f_tps = open("csvs/one_mc_baseline_{}_tps.csv".format(mode))
		f_rt = open("csvs/one_mc_baseline_{}_rt.csv".format(mode))

		tps = get_vals(f_tps)
		r_time = get_vals(f_rt)
		plt.plot(tps, r_time, label = "Load: {}".format(mode))

	plt.xlim(xmin = 0)
	plt.ylim(ymin = 0)
	plt.xlabel("Throughput (Ops/Sec)")
	plt.ylabel("Response Time (msec)")
	plt.legend()
	plt.savefig("2a_interactive_law.png")

	plt.figure()
	plt.title("Interactive Law for Two MC Experiments")

	for mode in modes:
		f_tps = open("csvs/two_mc_baseline_{}_tps.csv".format(mode))
		f_rt = open("csvs/two_mc_baseline_{}_rt.csv".format(mode))

		tps = get_vals(f_tps)
		r_time = get_vals(f_rt)
		plt.plot(tps, r_time, label = "Load: {}".format(mode))

	plt.xlim(xmin = 0)
	plt.ylim(ymin = 0)
	plt.xlabel("Throughput (Ops/Sec)")
	plt.ylabel("Response Time (msec)")
	plt.legend()
	plt.savefig("2b_interactive_law.png")