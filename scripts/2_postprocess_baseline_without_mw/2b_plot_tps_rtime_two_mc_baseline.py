from __future__ import print_function
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# sns.set()
plt.figure()
plt.title("Response Time vs. Num of Virtual Clients \n (Two Server Baseline)")

num_vc = []
val    = [] 
std    = []

with open("csvs/two_mc_baseline_r-o_rt.csv") as f:
	for line in f:
		vc, v, s = [float(x) for x in line.strip().split(",")][:3]
		num_vc.append(vc)
		val.append(v)
		std.append(s)
plt.errorbar(x = num_vc, y = val, yerr = std, label = "Read-Only", capsize = 2)

num_vc = []
val    = [] 
std    = []
with open("csvs/two_mc_baseline_w-o_rt.csv") as f:
	for line in f:
		vc, v, s = [float(x) for x in line.strip().split(",")][:3]
		num_vc.append(vc)
		val.append(v)
		std.append(s)
plt.errorbar(x = num_vc, y = val, yerr = std, label = "Write-Only", capsize = 2)

plt.grid(linestyle = "dotted")
plt.ylabel("Average Response Time (msec)")
plt.xlabel("Number of Virtual Clients")
plt.legend()
# plt.yticks([0] + val)
plt.xticks([0] + num_vc)
plt.ylim(ymin=0)

plt.savefig("2b_two_mc_rt.png")

plt.figure()
plt.title("Throughput vs. Num of Virtual Clients \n (Two Server Baseline)")

num_vc = []
val    = [] 
std    = []

with open("csvs/two_mc_baseline_r-o_tps.csv") as f:
	for line in f:
		vc, v, s = [float(x) for x in line.strip().split(",")][:3]
		num_vc.append(vc)
		val.append(v)
		std.append(s)
# plt.errorbar(x = num_vc, y = np.asarray(val) / 100., yerr = np.asarray(std) / 1000., label = "Read-Only", capsize = 2)
plt.errorbar(x = num_vc, y = np.asarray(val), yerr = np.asarray(std), label = "Read-Only", capsize = 2)

num_vc = []
val    = [] 
std    = []
with open("csvs/two_mc_baseline_w-o_tps.csv") as f:
	for line in f:
		vc, v, s = [float(x) for x in line.strip().split(",")][:3]
		num_vc.append(vc)
		val.append(v)
		std.append(s)
# plt.errorbar(x = num_vc, y = np.asarray(val) / 100., yerr = np.asarray(std) / 1000., label = "Write-Only", capsize = 2)
plt.errorbar(x = num_vc, y = np.asarray(val), yerr = np.asarray(std), label = "Write-Only", capsize = 2)


plt.grid(linestyle = "dotted")
plt.ylabel("Throughput (reqs/sec)")
plt.xlabel("Number of Virtual Clients")
plt.legend()

# plt.yticks([0] + np.asarray(val) / 100.)
plt.xticks([0] + num_vc)
plt.ylim(ymin=0)

plt.savefig("2b_two_mc_tps.png")