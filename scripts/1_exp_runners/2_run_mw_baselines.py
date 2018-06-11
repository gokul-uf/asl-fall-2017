from __future__ import print_function
from os import system
from time import sleep

# system = print
# sleep = print

num_reps = 3
def print_line():
	print("=========================================================================")

def populate_mc(mt_ip, server_ip):
	# populate MCs with keys to avoid get misses
	print("Populating MC with keys")
	command = "ssh {} 'memtier_benchmark -s {} -p 6969 -P memcache_text -n allkeys --ratio 1:0".format(mt_ip, server_ip) \
			   + " --key-maximum 10000 --hide-histogram --expiry-range 99999-100000 -d 1024 --key-pattern=S:S> /dev/null 2>&1'"
	system(command)
	print("MC population completed!")	

def run_one_mw_base_line():
	mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com"
	mw_ip = "sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com"
	client_range = [2, 4, 8, 16, 32, 64, 128]
	thread_range = [8, 16, 32, 64]

	# create the log directory
	print("creating log directories")
	system("ssh {} 'mkdir /home/sgokula/one_mw_base_line_log'".format(mt_ip))

	# Run ping tests
	print("Running ping tests")
	system("ssh {} 'ping -c 5 10.0.0.4 > /home/sgokula/one_mw_base_line_log/ping_to_mw.txt'".format(mt_ip))
	system("ssh {} 'ping -c 5 10.0.0.6 > /home/sgokula/one_mw_base_line_log/ping_to_mc.txt'".format(mt_ip))

	# Populate MC with keys
	populate_mc(mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com",
				server_ip = "10.0.0.6")

	# Do the write-only load

	print_line()
	print("running single-mw write-only load experiments")
	print_line()

	for num_clients in client_range:
		for thread_count in thread_range:
			for i in range(1, num_reps+1):
				print("num_clients: {}, thread_count: {}, rep: {}".format(num_clients, thread_count, i))

				# Finally run the actual experiment -_- -.-'
				print("starting the middleware")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s false -m 10.0.0.6:6969 </dev/null >/dev/null 2>&1 &'".format(thread_count))

				print("sleep for 20secs before running MT")
				sleep(20)				
				
				# Start off dstat
				print("starting dstat")
				system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ip) \
						+ "--output /home/sgokula/one_mw_base_line_log/dstat_w-o_c-{}_t-{}_rep-{}.csv ".format(num_clients, thread_count, i) \
						+ "5 18 >/dev/null </dev/null 2>&1 &'")

				print("running config")
				system("ssh {} 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 2 -c {} --ratio 1:0 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/one_mw_base_line_log/mt_w-o_c-{}_t-{}_rep-{}.json > /dev/null 2>&1'".format(num_clients, thread_count, i))

				print("killing MW")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'killall java'")

				# Rename / move the log files in MC to some place else, because it doesn't keep track of reps, or VC
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/one-mw_w-o_c-{}_t-{}_rep-{}_log'".format(num_clients, thread_count, i))

				# Sleep for 5 seconds
				print("sleeping for 5 secs before next config")
				sleep(5)

	# Do the read-only loads

	print_line()
	print("running single-mw read-only load experiments")
	print_line()

	for num_clients in client_range:
		for thread_count in thread_range:
			for i in range(1, num_reps+1):
				print("num_clients: {}, thread_count: {}, rep: {}".format(num_clients, thread_count, i))
				
				# Finally run the actual experiment -_- -.-'
				print("starting the middleware")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s false -m 10.0.0.6:6969 >/dev/null </dev/null 2>&1 &'".format(thread_count))


				print("sleep for 20secs before running MT")
				sleep(20)


				# Start off dstat
				print("starting dstat")
				system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ip) \
						+ "--output /home/sgokula/one_mw_base_line_log/dstat_r-o_c-{}_t-{}_rep-{}.csv ".format(num_clients, thread_count, i) \
						+ "5 18 >/dev/null </dev/null 2>&1 &'")


				print("running config")
				system("ssh {} 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 2 -c {} -d 1024 --ratio 0:1 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/one_mw_base_line_log/mt_r-o_c-{}_t-{}_rep-{}.json > /dev/null 2>&1'".format(num_clients, thread_count, i))

				print("killing MW")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'killall java'")

				# Move the log  files in MC to some place else, because it doesn't keep track of reps, or VC
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/one-mw_r-o_c-{}_t-{}_rep-{}_log'".format(num_clients, thread_count, i))

				# Sleep for 5 seconds
				print("sleeping for 5 secs before next config")
				sleep(5)


def run_two_mw_base_line():
	mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com"
	mc_ips = "sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com"

	client_range = [2, 4, 8, 16, 32, 64, 128]
	thread_range = [8, 16, 32, 64]

	print("start the extra MW VM")
	system("az vm start --name foraslvms5 --resource-group ASL")

	# wait 2 mins to make sure it's properly up
	print("sleeping for 2 minutes before running exps")
	sleep(120)

	# create the log directory
	print("creating log directories")
	system("ssh {} 'mkdir /home/sgokula/two_mw_base_line_log'".format(mt_ip))

	# Run ping tests
	print("Running ping tests")
	system("ssh {} 'ping -c 5 10.0.0.4 > /home/sgokula/two_mw_base_line_log/ping_mw_1.txt'".format(mt_ip))
	system("ssh {} 'ping -c 5 10.0.0.8 > /home/sgokula/two_mw_base_line_log/ping_mw_2.txt'".format(mt_ip))
	system("ssh {} 'ping -c 5 10.0.0.6 > /home/sgokula/two_mw_base_line_log/ping_mc.txt'".format(mt_ip))

	# Populate MC with keys
	populate_mc(mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com",
				server_ip = "10.0.0.6")

	# Do the write-only load
	print_line()
	print("running two-mw write-only load experiments")
	print_line()

	for num_clients in client_range:
		for thread_count in thread_range:
			for i in range(1, num_reps+1):
				print("num_clients: {}, thread_count: {}, rep: {}".format(num_clients, thread_count, i))

				print("starting the middleware")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s false -m 10.0.0.6:6969 >/dev/null </dev/null 2>&1 &'".format(thread_count))
				system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.8 -p 6969 -t {} -s false -m 10.0.0.6:6969 >/dev/null </dev/null 2>&1 &'".format(thread_count))

				print("sleep for 20secs before running MT")
				sleep(20)

				# Start off dstat
				print("starting dstat")
				system("ssh {} 'dstat -cmn --nocolor ".format(mt_ip) \
						+ "--output /home/sgokula/two_mw_base_line_log/dstat_w-o_c-{}_t-{}_rep-{}.csv ".format(num_clients, thread_count, i) \
						+ "5 20 >/dev/null </dev/null 2>&1 &'")


				# Finally run the actual experiment -_- -.-'

				print("running config")
				system("ssh {} 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 1 -c {} --ratio 1:0 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/two_mw_base_line_log/mt_w-o_c-{}_t-{}_rep-{}_mt-1.json </dev/null >/dev/null 2>&1 &'".format(num_clients, thread_count, i))
				system("ssh {} 'memtier_benchmark -s 10.0.0.8 -p 6969 -P memcache_text -t 1 -c {} --ratio 1:0 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/two_mw_base_line_log/mt_w-o_c-{}_t-{}_rep-{}_mt-2.json </dev/null >/dev/null 2>&1'".format(num_clients, thread_count, i))


				print("killing memcached")
				system("parallel-ssh -t 0 -H '{}' 'killall java' ".format(mc_ips))

				# Move / rename the log files in MC to some place else, because it doesn't keep track of reps, or VC
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/two-mw_w-o_c-{}_t-{}_rep-{}_mw-1_log'".format(num_clients, thread_count, i))
				system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/two-mw_w-o_c-{}_t-{}_rep-{}_mw-2_log'".format(num_clients, thread_count, i))

				# Sleep for 5 seconds
				print("sleeping for 5 secs before next config")
				sleep(5)

	# Do the read-only load
	print_line()
	print("running two-mw read-only load experiments")
	print_line()

	for num_clients in client_range:
		for thread_count in thread_range:
			for i in range(1, num_reps+1):
				print("num_clients: {}, thread_count: {}, rep: {}".format(num_clients, thread_count, i))

				print("starting the middleware")
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s false -m 10.0.0.6:6969 >/dev/null </dev/null 2>&1 &'".format(thread_count))
				system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.8 -p 6969 -t {} -s false -m 10.0.0.6:6969 >/dev/null </dev/null 2>&1 &'".format(thread_count))

				print("sleep for 20secs before running MT")
				sleep(20)

				# Start off dstat
				print("starting dstat")
				system("ssh {} 'dstat -cmn --nocolor ".format(mt_ip) \
						+ "--output /home/sgokula/two_mw_base_line_log/dstat_r-o_c-{}_t-{}_rep-{}.csv ".format(num_clients, thread_count, i) \
						+ "5 20 >/dev/null </dev/null 2>&1 &'")


				# Finally run the actual experiment -_- -.-'

				print("running config")
				system("ssh {} 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 1 -c {} --ratio 0:1 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/two_mw_base_line_log/mt_r-o_c-{}_t-{}_rep-{}_mt-1.json </dev/null >/dev/null 2>&1 &'".format(num_clients, thread_count, i))
				system("ssh {} 'memtier_benchmark -s 10.0.0.8 -p 6969 -P memcache_text -t 1 -c {} --ratio 0:1 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
						+ "--json-out-file /home/sgokula/two_mw_base_line_log/mt_r-o_c-{}_t-{}_rep-{}_mt-2.json </dev/null >/dev/null 2>&1'".format(num_clients, thread_count, i))


				print("killing middleware")
				system("parallel-ssh -t 0 -H '{}' 'killall java' ".format(mc_ips))

				# Move / rename the log files in MC to some place else, because it doesn't keep track of reps, or VC
				system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/two-mw_r-o_c-{}_t-{}_rep-{}_mw-1_log'".format(num_clients, thread_count, i))
				system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/two-mw_r-o_c-{}_t-{}_rep-{}_mw-2_log'".format(num_clients, thread_count, i))

				# Sleep for 5 seconds
				print("sleeping for 5 secs before next config")
				sleep(5)


if __name__ == "__main__":
	# Start the VMs
	print("Starting VMs")
	system("az vm start --name foraslvms1 --resource-group ASL")
	system("az vm start --name foraslvms4 --resource-group ASL")
	system("az vm start --name foraslvms6 --resource-group ASL")

	# wait 2 mins before startin exps to make sure everything's up
	print("sleeping for 2 minutes before running exps")
	sleep(120)

	# Start MC instance on the MC VM
	print("Starting an MC instance on the VM")
	system('ssh sgokula@sgokulaforaslvms6.westeurope.cloudapp.azure.com "memcached -t 1 -p 6969 >/dev/null </dev/null 2>&1 & "')

	run_one_mw_base_line()
	run_two_mw_base_line()
	
	print("shut down everything!")
	system("az vm deallocate --name foraslvms1 --resource-group ASL")
	system("az vm deallocate --name foraslvms4 --resource-group ASL")
	system("az vm deallocate --name foraslvms5 --resource-group ASL")
	system("az vm deallocate --name foraslvms6 --resource-group ASL")
