'''
Goes through a folder containing folders with
raw logs from each config run of a MW and spits 
out one JSON per config avg_q_len, wait_time, tps, rtime
It does not combine across reps though

Things extracted
2. average queue length
4. Throughput

1. time in queue
3. response time
5. time waiting for MC
6. Worker Thread service time
7. TODO net thread service time 
8. TODO worker thread preprocessing
9. TODO worker thread postprocessing
'''


from __future__ import print_function
from __future__ import division

from glob import glob
import json
import numpy as np
import os
import sys
from tqdm import tqdm

def process_thread_file(thread_file):
	thread_file = os.path.abspath(thread_file)
	f = open(thread_file)

	lines = f.readlines()
	lines = [line.strip().split(" ") for line in lines]
	if "set-tps" in thread_file or "get-exp" in thread_file or "one-mw" in thread_file or "two-mw" in thread_file:
		lines = [[float(x) for x in line[1:]] for line in lines]
	else:
		lines = [[float(x) for x in line] for line in lines]

	start_time = lines[0][0]
	five_secs = 5000000000
	end_time = lines[-1][0]

	resp_time           = []
	time_in_queue       = []

	wt_preprocess_time  = []
	wt_postprocess_time = []

	nt_service_time     = []	
	wt_service_time     = []

	wait_for_mc         = []
	

	for line in lines:
		t = line[0]
		if t - start_time > five_secs and end_time - t >= five_secs: # Throw away first five and last five secs as warm up and cool down phases
			time_request_created = line[0]
			time_enqueued = line[1]
			time_dequeued = line[2]
			time_start_send_to_mc = line[3]
			time_get_from_mc = line[6]
			time_sent_back_start = line[7]
			time_sent_back_complete = line[8]
			
			resp_time.append(time_sent_back_complete - time_request_created)
			time_in_queue.append(time_dequeued - time_enqueued)
			
			wt_preprocess_time.append(time_start_send_to_mc - time_dequeued)
			wt_postprocess_time.append(time_sent_back_start - time_get_from_mc)

			nt_service_time.append(time_enqueued - time_request_created)
			wt_service_time.append(time_sent_back_start - time_dequeued)

			wait_for_mc.append(time_get_from_mc - time_start_send_to_mc)
			


	tps = len(lines) / 70.  # requests/sec

	r_time = np.mean(resp_time)
	q_time = np.mean(time_in_queue)

	wt_preprocess_time = np.mean(np.abs(wt_preprocess_time))
	wt_postprocess_time = np.mean(np.abs(wt_postprocess_time))

	nt_service_time = np.mean(np.abs(nt_service_time))
	wt_service_time = np.mean(wt_service_time)

	mc_wait_time = np.mean(wait_for_mc)

	return tps, r_time, q_time, wt_preprocess_time, wt_postprocess_time, nt_service_time, wt_service_time, mc_wait_time # 8 items

	# return wait_time, r_time, tps, mc_wait_time, wt_service_time, nt_service_time, wt_preprocess_time, wt_postprocess_time

def summarize_folder(folder):
	folder = os.path.abspath(folder)
	error_files = glob("{}/*.error".format(folder))
	for error_file in error_files:
		if os.path.getsize(error_file) != 0:
			print("WARN: {} is not empty, please check it, nothing done in this folder".format(error_file))
			return
	length_file = glob("{}/*.length".format(folder))
	print("processing {}".format(os.path.basename(folder)))
	lens = []
	for line in open(length_file[0]):
		line = line.strip()
		lens.append(float(line))

	avg_len = np.mean(lens)

	thread_files = glob("{}/*.info".format(folder))
	thread_files = [t for t in thread_files if not t.endswith("frontend.info")]

	thread_tps = []

	thread_r_time = []
	thread_q_time = []

	thread_wt_preprocess_time  = []
	thread_wt_postprocess_time = []
	
	thread_nt_service_time = []
	thread_wt_service_time = []

	thread_mc_wait = []
	
	print("processing the thread files")
	for i, thread_file in tqdm(enumerate(thread_files), total = len(thread_files)):
		# tps, r_time, q_time, wt_preprocess_time, wt_postprocess_time, nt_service_time, wt_service_time, mc_wait_time
		t_tps, t_r_time, t_q_time, t_wt_preprocess_time, t_wt_postprocess_time, t_nt_service_time, t_wt_service_time, t_mc_wait_time  = process_thread_file(thread_file)

		thread_tps.append(t_tps)

		thread_r_time.append(t_r_time)
		thread_q_time.append(t_q_time)

		thread_wt_preprocess_time.append(t_wt_preprocess_time)
		thread_wt_postprocess_time.append(t_wt_postprocess_time)

		thread_nt_service_time.append(t_nt_service_time)
		thread_wt_service_time.append(t_wt_service_time)

		thread_mc_wait.append(t_mc_wait_time)

		# thread_wait_time.append(wait_time)
		# thread_r_time.append(r_time)
		# thread_tps.append(tps)
		# thread_mc_wait.append(mc_wait)
		# thread_service_time.append(wt_s_time)

	info_dict = {}
	info_dict["avg_q_len"]       = avg_len
	
	info_dict["tps"]             = np.sum(thread_tps)

	info_dict["r_time"]          = np.mean(thread_r_time)
	info_dict["quing_time"]      = np.mean(thread_q_time)

	info_dict["wt_preprocess_time"]  = np.mean(thread_wt_preprocess_time)
	info_dict["wt_postprocess_time"] = np.mean(thread_wt_postprocess_time)

	info_dict["nt_service_time"] = np.mean(thread_nt_service_time)
	info_dict["wt_service_time"] = np.mean(thread_wt_service_time)

	info_dict["mc_wait_time"]    = np.mean(thread_mc_wait)
	
 	parent_dir = os.path.dirname(folder)
 	file_name = os.path.basename(folder)[:-4] + ".json"

 	json.dump(info_dict, open(os.path.join(parent_dir, file_name), "w"), indent = 0)

if __name__ == "__main__":
	base_dir = sys.argv[1]
	base_dir = os.path.abspath(base_dir)
	ls = glob(base_dir + "/*")
	ls.sort()
	for file in ls:
		if os.path.isdir(file):
			summarize_folder(file)
