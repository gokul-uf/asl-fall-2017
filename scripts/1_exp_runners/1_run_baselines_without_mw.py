from __future__ import print_function
from os import system
from time import sleep

# system = print

num_reps = 3
def print_line():
	print("=========================================================================")

def populate_mc(mt_ip, server_ip):
	# populate MCs with keys to avoid get misses
	print("Populating MC with keys")
	# TODO how to ensure all keys have been written? -n allkeys doesn't seem to help

	command = "ssh {} 'memtier_benchmark -s {} -p 6969 -P memcache_text -n allkeys --ratio 1:0".format(mt_ip, server_ip) \
			   + " --key-maximum 10000 --hide-histogram --expiry-range 99999-100000 -d 1024 --key-pattern=S:S > /dev/null 2>&1'"
	system(command)
	print("MC population completed!")	

def run_one_server_base_line():
	mt_ips = ("sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com "
			  "sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com "
			  "sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com")

	# client_range = [1] + range(10, 151, 10) # TODO What's the best client_range?
	client_range = [1] + range(5, 155, 10)

	# Start the MT VMs
	print("Starting VMs")
	system("az vm start --name foraslvms1 --resource-group ASL")
	system("az vm start --name foraslvms2 --resource-group ASL")
	system("az vm start --name foraslvms3 --resource-group ASL")

	# Start the MC VM
	system("az vm start --name foraslvms6 --resource-group ASL")

	# wait 2 mins before startin exps to make sure everything's up
	print("sleeping for 2 minutes before running exps")
	sleep(120)

	# Start MC instance on the MC VM
	print("Starting an MC instance on the VM")
	system('ssh sgokula@sgokulaforaslvms6.westeurope.cloudapp.azure.com "memcached -t 1 -p 6969 >/dev/null </dev/null 2>&1 & "')

	# create the log directory
	print("creating log directories")
	system("parallel-ssh -H '{}' 'mkdir /home/sgokula/one_server_base_line_log'".format(mt_ips))

	# Run ping tests
	print("Running ping tests")
	system("parallel-ssh -t 0 -H '{}' 'ping -c 5 10.0.0.6 > /home/sgokula/one_server_base_line_log/ping_$HOSTNAME.txt'".format(mt_ips))

	# Populate MC with keys
	populate_mc(mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com",
				server_ip = "10.0.0.6")

	# Do the write-only load

	print_line()
	print("running single-server write-only load experiments")
	print_line()

	for num_clients in client_range:

		for i in range(1, num_reps+1):
			print("num_clients: {}, rep: {}".format(num_clients, i))
			
			# Start off dstat
			print("starting dstat")
			system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ips) \
					+ "--output /home/sgokula/one_server_base_line_log/dstat_w-o_c-{}_rep-{}_$HOSTNAME.csv ".format(num_clients, i) \
					+ "5 18 >/dev/null </dev/null 2>&1 &'")

			# Finally run the actual experiment -_- -.-'
			print("running config single-server write-only, num_clients: {}, rep: {}".format(num_clients, i))
			system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.6 -p 6969 -P memcache_text -t 2 -c {} -d 1024 --ratio 1:0 --test-time 80 ".format(mt_ips, num_clients) \
					+ "--json-out-file /home/sgokula/one_server_base_line_log/mt_w-o_c-{}_rep-{}_$HOSTNAME.json > /dev/null 2>&1'".format(num_clients, i))

			# Sleep for 5 seconds
			print("sleeping for 5 secs before next config")
			sleep(5)

	# Do the read-only loads

	print_line()
	print("running single-server read-only load experiments")
	print_line()

	for num_clients in client_range:

		for i in range(1, num_reps+1):
			print("num_clients: {}, rep: {}".format(num_clients, i))
			
			# Start off dstat
			print("starting dstat")
			system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ips) \
					+ "--output /home/sgokula/one_server_base_line_log/dstat_r-o_c-{}_rep_{}_$HOSTNAME.csv ".format(num_clients, i) \
					+ "5 18 >/dev/null </dev/null 2>&1 &'")

			# Finally run the actual experiment -_- -.-'
			print("running config single-server read-only num_clients: {}, rep: {}".format(num_clients, i))
			system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.6 -p 6969 -P memcache_text -t 2 -c {} -d 1024 --ratio 0:1 --test-time 80 ".format(mt_ips, num_clients) \
					+ "--json-out-file /home/sgokula/one_server_base_line_log/mt_r-o_c-{}_rep-{}_$HOSTNAME.json > /dev/null 2>&1'".format(num_clients, i))

			# Sleep for 5 seconds
			print("sleeping for 5 secs before next config")
			sleep(5)


def run_two_server_base_line():
	mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com"
	# client_range = [1] + range(10, 151, 10) # TODO What's the best client_range?
	client_range = [1] + range(5, 155, 10)

	print("start the extra MC VM")
	system("az vm start --name foraslvms7 --resource-group ASL")

	# wait 2 mins to make sure it's properly up
	print("sleeping for 2 minutes before running exps")
	sleep(120)

	print("start a new instance of MC on the new VM")
	system('ssh sgokula@sgokulaforaslvms7.westeurope.cloudapp.azure.com "memcached -t 1 -p 6969 >/dev/null </dev/null 2>&1 & "')

	# create the log directory
	print("creating log directories")
	system("ssh {} 'mkdir /home/sgokula/two_server_base_line_log'".format(mt_ip))

	# Run ping tests
	print("Running ping tests")
	system("ssh {} 'ping -c 5 10.0.0.6 > /home/sgokula/two_server_base_line_log/ping_mc_1.txt'".format(mt_ip))
	system("ssh {} 'ping -c 5 10.0.0.11 > /home/sgokula/two_server_base_line_log/ping_mc_2.txt'".format(mt_ip))

	# Populate MC with keys
	populate_mc(mt_ip = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com",
				server_ip = "10.0.0.11")

	# Do the write-only load
	print_line()
	print("running two-server write-only load experiments")
	print_line()

	for num_clients in client_range:

		for i in range(1, num_reps+1):
			print("num_clients: {}, rep: {}".format(num_clients, i))
			
			# Start off dstat
			print("starting dstat")
			system("ssh {} 'dstat -cmn --nocolor ".format(mt_ip) \
					+ "--output /home/sgokula/two_server_base_line_log/dstat_w-o_c-{}_rep-{}.csv ".format(num_clients, i) \
					+ "5 20 >/dev/null </dev/null 2>&1 &'")

			# Finally run the actual experiment -_- -.-'
			print("running config two-server write-only num_clients: {}, rep: {}".format(num_clients, i))
			system("ssh {} 'memtier_benchmark -s 10.0.0.6  -p 6969 -P memcache_text -t 1 -c {} --ratio 1:0 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
					+ "--json-out-file /home/sgokula/two_server_base_line_log/mt_w-o_c-{}_mt-1_rep-{}.json </dev/null >/dev/null 2>&1 &'".format(num_clients, i))
			system("ssh {} 'memtier_benchmark -s 10.0.0.11 -p 6969 -P memcache_text -t 1 -c {} --ratio 1:0 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
					+ "--json-out-file /home/sgokula/two_server_base_line_log/mt_w-o_c-{}_mt-2_rep-{}.json </dev/null >/dev/null 2>&1'".format(num_clients, i))

			# Sleep for 5 seconds
			print("sleeping for 5 secs before next config")
			sleep(5)

	# Do the read-only load
	print_line()
	print("running two-server read-only load experiments")
	print_line()

	for num_clients in client_range:

		for i in range(1, num_reps+1):
			print("num_clients: {}, rep: {}".format(num_clients, i))
			
			# Start off dstat
			print("starting dstat")
			system("ssh {} 'dstat -cmn --nocolor ".format(mt_ip) \
					+ "--output /home/sgokula/two_server_base_line_log/dstat_r-o_c-{}_rep-{}.csv ".format(num_clients, i) \
					+ "5 20 >/dev/null </dev/null 2>&1 &'")

			# Finally run the actual experiment -_- -.-'
			print("running config two-server read-only num_clients: {}, rep: {}".format(num_clients, i))
			system("ssh {} 'memtier_benchmark -s 10.0.0.6 -p 6969 -P memcache_text -t 1 -c {} --ratio 0:1 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
					+ "--json-out-file /home/sgokula/two_server_base_line_log/mt_r-o_c-{}_mt-1_rep-{}.json </dev/null >/dev/null 2>&1 &'".format(num_clients, i))
			system("ssh {} 'memtier_benchmark -s 10.0.0.11 -p 6969 -P memcache_text -t 1 -c {} --ratio 0:1 -d 1024 --test-time 80 ".format(mt_ip, num_clients) \
					+ "--json-out-file /home/sgokula/two_server_base_line_log/mt_r-o_c-{}_mt-2_rep-{}.json </dev/null >/dev/null 2>&1'".format(num_clients, i))

			# Sleep for 5 seconds
			print("sleeping for 5 secs before next config")
			sleep(5)

if __name__ == "__main__":
	run_one_server_base_line()

	# Shut down not required VMs
	print("shut down not required MTs")
	system("az vm deallocate --name foraslvms2 --resource-group ASL")
	system("az vm deallocate --name foraslvms3 --resource-group ASL")
	
	run_two_server_base_line()
	
	print("shut down everything!")
	system("az vm deallocate --name foraslvms1 --resource-group ASL")
	system("az vm deallocate --name foraslvms6 --resource-group ASL")
	system("az vm deallocate --name foraslvms7 --resource-group ASL")
