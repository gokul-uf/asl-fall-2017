from __future__ import print_function
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

num_threads = [8, 16, 32, 64]
# sns.set()
plt.figure()
plt.title("Throughput vs. Num of Virtual Clients")
for num_thread in num_threads: 
	num_vc = []
	val    = []
	std    = []

	with open("csvs/write_tps_t_{}_tps.csv".format(num_thread)) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = "{} Threads".format(num_thread), capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Throughput (Ops / sec)")
plt.xlabel("Number of Virtual Clients")
plt.legend()
# plt.yticks([0] + val)
plt.ylim(ymin=0)
plt.xticks([0] + num_vc)
plt.savefig("4_set_tps_tps.png")


plt.figure()
plt.title("Response Time vs. Num of Virtual Clients")
for num_thread in num_threads: 
	num_vc = []
	val    = []
	std    = []

	with open("csvs/write_tps_t_{}_rt.csv".format(num_thread)) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = "{} Threads".format(num_thread), capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Response Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.legend()
plt.xticks([0] + num_vc)
plt.savefig("4_set_tps_rt.png")

plt.figure()
plt.title("Queueing Time vs. Num of Virtual Clients")
for num_thread in num_threads: 
	num_vc = []
	val    = []
	std    = []

	with open("csvs/write_tps_t_{}_q_wt.csv".format(num_thread)) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = "{} Threads".format(num_thread), capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Queueing Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.legend()
plt.xticks([0] + num_vc)
plt.savefig("4_set_tps_q_wt.png")


plt.figure()
plt.title("Waiting for MC Time vs. Num of Virtual Clients")
for num_thread in num_threads: 
	num_vc = []
	val    = []
	std    = []

	with open("csvs/write_tps_t_{}_mc_wait.csv".format(num_thread)) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = "{} Threads".format(num_thread), capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Waiting Time (ms)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.legend()
plt.xticks([0] + num_vc)
plt.savefig("4_set_tps_mc_wt.png")

plt.figure()
plt.title("Queue Length vs. Num of Virtual Clients")
for num_thread in num_threads: 
	num_vc = []
	val    = []
	std    = []

	with open("csvs/write_tps_t_{}_q_len.csv".format(num_thread)) as f:
		for line in f:
			vc, v, s = [float(x) for x in line.strip().split(",")][:3]
			num_vc.append(vc)
			val.append(v)
			std.append(s)
	plt.errorbar(x = num_vc, y = val, yerr = std, label = "{} Threads".format(num_thread), capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Queue Length (num requests)")
plt.xlabel("Number of Virtual Clients")
plt.ylim(ymin=0)
plt.legend()
plt.xticks([0] + num_vc)
plt.savefig("4_set_tps_q_len.png")