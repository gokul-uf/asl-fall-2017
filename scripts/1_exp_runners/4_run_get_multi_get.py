from __future__ import print_function
from os import system
from time import sleep
# system = print
# sleep = print

'''
3 MT, 2 MW, 3 MC
'''

num_reps = 3
num_thread = 64
shard_modes = [True, False]
multi_gets = [1, 3, 6, 9]

def start_vms():
    print("starting VMs")
    for i in range(1, 9):
        print("Starting foraslvms{}".format(i))
        system("az vm start --name foraslvms{} --resource-group ASL".format(i))
    print("All VMs started")

def stop_vms():
    print("stopping VMs")
    for i in range(1, 9):
        print("Stopping foraslvms{}".format(i))
        system("az vm deallocate --name foraslvms{} --resource-group ASL".format(i))
    print("All VMs shutdown")

def start_mc():
    print("Starting an MC instance on the VM") 
    for i in range(6, 9):
        print("Starting on foraslvms{}".format(i))
        system('ssh sgokula@sgokulaforaslvms{}.westeurope.cloudapp.azure.com "memcached -t 1 -p 6969 >/dev/null </dev/null 2>&1 & "'.format(i))
    print("MC Instances running")

def make_dirs():
    mt_ips = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com"
    print("creating dirs in MT")
    system("parallel-ssh -H '{}' 'mkdir /home/sgokula/gets_exp_log'".format(mt_ips))

def ping_tests():
    print("Runing ping tests")
    mt_ips = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com"
    

    mc_ips = [
        "10.0.0.6",
        "10.0.0.11",
        "10.0.0.7"
    ]

    mw_ips = [
            "10.0.0.4",
            "10.0.0.8"
    ]

    print("pinging MC instances")
    for i, mc_ip in enumerate(mc_ips):
        system("parallel-ssh -t 0 -H '{}' 'ping -c 5 {} > /home/sgokula/gets_exp_log/ping_mc_{}_$HOSTNAME.txt'".format(mt_ips, mc_ip, i))

    print("pinging MW instances")
    for i, mw_ip in enumerate(mw_ips): 
        system("parallel-ssh -t 0 -H '{}' 'ping -c 5 {} > /home/sgokula/gets_exp_log/ping_mw_{}_$HOSTNAME.txt'".format(mt_ips, mw_ip, i))
    print("ping tests completed")

def populate_all_mc():
    print("Populating MCs with keys")
    mt_ips = [
        "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com",
        "sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com",
        "sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com"
    ]

    mc_ips = [
        "10.0.0.6",
        "10.0.0.11",
        "10.0.0.7"
    ]

    for mt_ip, mc_ip in zip(mt_ips, mc_ips):
        print("populating {} with {}".format(mc_ip, mt_ip))
        command = "ssh {} 'memtier_benchmark -s {} -p 6969 -P memcache_text -n allkeys --ratio 1:0".format(mt_ip, mc_ip) \
             + " --key-maximum 10000 --hide-histogram --expiry-range 99999-100000 -d 1024 --key-pattern=S:S> /dev/null 2>&1'"
        system(command)
    print("MC population completed!")

def run_config(shard_mode, num_multi_get, rep):
    mt_ips = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com"
    mw_ips = "sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com"

    # start MWs
    print("starting the middleware")
    system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s {} -m 10.0.0.6:6969 10.0.0.7:6969 10.0.0.11:6969 >/dev/null </dev/null 2>&1 &'".format(num_thread, shard_mode))
    system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.8 -p 6969 -t {} -s {} -m 10.0.0.6:6969 10.0.0.7:6969 10.0.0.11:6969 >/dev/null </dev/null 2>&1 &'".format(num_thread, shard_mode))

    # sleep to let the MW establish connections
    print("sleep for 20secs before running MT")
    sleep(20)

    # start dstat
    print("starting dstat")
    system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ips) \
            + "--output /home/sgokula/gets_exp_log/dstat_s-{}_g-{}_rep-{}_$HOSTNAME.csv ".format(shard_mode, num_multi_get, rep) \
            + "5 20 >/dev/null </dev/null 2>&1 &'")

    # run the config, MT
    print("running config") # ratio=1:8 --multi-key-get=8
    system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 1 -c 2 --ratio 1:{} --multi-key-get={} ".format(mt_ips, num_multi_get, num_multi_get) \
        + " --test-time 80 --key-maximum 10000 -d 1024 --json-out-file /home/sgokula/gets_exp_log/mt_s-{}_g-{}_rep-{}_mw-1_$HOSTNAME.json </dev/null >/dev/null 2>&1 &'".format(shard_mode, num_multi_get, rep))

    system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.8 -p 6969 -P memcache_text -t 1 -c 2 --ratio 1:{} --multi-key-get={} ".format(mt_ips, num_multi_get, num_multi_get) \
        + " --test-time 80 --key-maximum 10000 -d 1024 --json-out-file /home/sgokula/gets_exp_log/mt_s-{}_g-{}_rep-{}_mw-2_$HOSTNAME.json </dev/null >/dev/null 2>&1 '".format(shard_mode, num_multi_get, rep))

    # kill middleware, RIP
    print("killing middleware")
    system("parallel-ssh -t 0 -H '{}' 'killall java' ".format(mw_ips))

    # Move / rename the log files in MC to some place else, because it doesn't keep track of reps, or VC
    print("moving MW logs")
    system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/gets-exp_s-{}_g-{}_rep-{}_mw-1_log'".format(shard_mode, num_multi_get, rep))
    system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/gets-exp_s-{}_g-{}_rep-{}_mw-2_log'".format(shard_mode, num_multi_get, rep))

def run_exp():
    count = 1
    for shard_mode in shard_modes:
        for multi_get_size in multi_gets:
            for rep in range(1, num_reps+1):
                print("runing config {} / 24, shard: {}, multi_get_size {}, rep: {}".format(count, shard_mode, multi_get_size, rep))
                run_config(shard_mode, multi_get_size, rep)
                count += 1
                # Sleep for 5 seconds
                print("sleeping for 5 secs before next config")
                sleep(5)

if __name__ == "__main__":
    start_vms()
    print("sleeping for 2 minutes before starting experiments")
    sleep(120)
    start_mc()
    populate_all_mc()
    make_dirs()
    ping_tests()
    run_exp()
    stop_vms()