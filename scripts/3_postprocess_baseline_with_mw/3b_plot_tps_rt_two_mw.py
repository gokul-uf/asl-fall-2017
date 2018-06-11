from __future__ import print_function
from __future__ import division
from glob import glob
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

thread_range = [8, 16, 32, 64]

def extract_n_plot(filename, label):
	num_vc = []
	val = []
	std = []
	with open(filename) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = label, capsize = 2)

plt.figure()
plt.title("Response Time vs. Num of Virtual Clients \n (Read-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_r-o_t_{}_rt.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylabel("Response Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.savefig("3b_two-mw_r-o_rt.png")

plt.figure()
plt.title("Throughput vs. Num of Virtual Clients \n (Read-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_r-o_t_{}_tps.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylabel("Throughput (request / second)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.savefig("3b_two-mw_r-o_tps.png")

plt.figure()
plt.title("Queueing Time vs. Num of Virtual Clients \n (Read-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_r-o_t_{}_wt.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylabel("Queueing Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.savefig("3b_two-mw_r-o_wt.png")

plt.figure()
plt.title("Response Time vs. Num of Virtual Clients \n (Write-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_w-o_t_{}_rt.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylim(ymin=0)
plt.ylabel("Response Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.savefig("3b_two-mw_w-o_rt.png")

plt.figure()
plt.title("Throughput vs. Num of Virtual Clients \n (Write-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_w-o_t_{}_tps.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylim(ymin=0)
plt.ylabel("Throughput (request / second)")
plt.xlabel("Number of Virtual Clients")
plt.savefig("3b_two-mw_w-o_tps.png")

plt.figure()
plt.title("Queueing Time vs. Num of Virtual Clients \n (Write-Only Two Middleware Baseline)")
for num_thread in thread_range:
	file = "csvs/two_mw_baseline_w-o_t_{}_wt.csv".format(num_thread)
	extract_n_plot(filename = file, label = "{} Worker Threads".format(num_thread))
plt.legend()
plt.grid(linestyle = "dotted")
plt.ylim(ymin=0)
plt.ylabel("Queueing Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.savefig("3b_two-mw_w-o_wt.png")