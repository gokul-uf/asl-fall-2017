from __future__ import print_function
from __future__ import division
from os import system
from time import sleep
# system = print
# sleep = print

num_reps = 3

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
    system("parallel-ssh -H '{}' 'mkdir /home/sgokula/2k_exp_log'".format(mt_ips))

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
        system("parallel-ssh -t 0 -H '{}' 'ping -c 5 {} > /home/sgokula/2k_exp_log/ping_mc_{}_$HOSTNAME.txt'".format(mt_ips, mc_ip, i))

    print("pinging MW instances")
    for i, mw_ip in enumerate(mw_ips): 
        system("parallel-ssh -t 0 -H '{}' 'ping -c 5 {} > /home/sgokula/2k_exp_log/ping_mw_{}_$HOSTNAME.txt'".format(mt_ips, mw_ip, i))
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

def run_exp():
    count = 1
    modes = ["w-o", "r-w", "r-o"]
    num_mc_range = [2, 3]
    num_mw_range = [1, 2]
    w_t_range = [8, 32]
    for mode in modes:
        for num_mc in num_mc_range:
            for num_mw in num_mw_range:
                for w_t in w_t_range:
                    for rep in range(1, num_reps + 1):
                        print("Running config {} / 72: Mode: {}, num_mc: {}, num_mw: {}, w_t: {}, rep: {}".format(count, mode, num_mc, num_mw, w_t, rep))
                        run_config(mode, num_mc, num_mw, w_t, rep)
                        count += 1
    # print("COUNT is: {}".format(count))

def get_mc_ips(num_mc):
    mc_ips = ["10.0.0.6:6969", "10.0.0.7:6969", "10.0.0.11:6969"]
    return " ".join(mc_ips[:num_mc])

def start_mw(num_mw, num_mc, w_t):
    mc_ips = get_mc_ips(num_mc)
    print("Starting first middleware")
    system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.4 -p 6969 -t {} -s False -m {} >/dev/null </dev/null 2>&1 &'".format(w_t, mc_ips))
    if num_mw == 2:
        print("Starting second middleware")
        system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'java -jar /home/sgokula/middleware-sgokula.jar -l 10.0.0.8 -p 6969 -t {} -s False -m {} >/dev/null </dev/null 2>&1 &'".format(w_t, mc_ips))
    print("middleware(s) started!")

def get_ratio(mode):
    if mode == "r-o":
        return "0:1"
    elif mode == "w-o":
        return "1:0"
    elif mode == "r-w":
        return "1:1"
    else:
        print("WARN: Illegal Value for mode, got: {}".format(mode))
        exit()

def run_config(mode, num_mc, num_mw, w_t, rep):
    mt_ips = "sgokula@sgokulaforaslvms1.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms2.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms3.westeurope.cloudapp.azure.com"
    mw_ips = "sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com"
    config_prefix = "{}_mc-{}_mw-{}_t-{}_rep-{}".format(mode, num_mc, num_mw, w_t, rep)

    ratio = get_ratio(mode)
    # start MW
    print("starting middleware")
    start_mw(num_mw, num_mc, w_t)

    # sleep to let the MW establish connections
    print("sleep for 20secs before running MT")
    sleep(20)

    # start dstat
    print("starting dstat")
    system("parallel-ssh -t 0 -H '{}' 'dstat -cmn --nocolor ".format(mt_ips) \
        + "--output /home/sgokula/2k_exp_log/dstat_{}_$HOSTNAME.csv ".format(config_prefix) \
        + "5 20 >/dev/null </dev/null 2>&1 &'")

    # run the config TODO
    print("running config")
    if num_mw == 1:
        system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 2 -c 32 --ratio {} ".format(mt_ips, ratio) \
        + " --test-time 80 -d 1024 --key-maximum 10000 --json-out-file /home/sgokula/2k_exp_log/mt_{}_$HOSTNAME.json </dev/null >/dev/null 2>&1'".format(config_prefix))
    else:
        system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.4 -p 6969 -P memcache_text -t 1 -c 32 --ratio {} ".format(mt_ips, ratio) \
        + " --test-time 80 -d 1024 --key-maximum 10000 --json-out-file /home/sgokula/2k_exp_log/mt_{}_mw-1_$HOSTNAME.json </dev/null >/dev/null 2>&1 &'".format(config_prefix))

        system("parallel-ssh -t 0 -H '{}' 'memtier_benchmark -s 10.0.0.8 -p 6969 -P memcache_text -t 1 -c 32 --ratio {} ".format(mt_ips, ratio) \
        + " --test-time 80 -d 1024 --key-maximum 10000 --json-out-file /home/sgokula/2k_exp_log/mt_{}_mw-2_$HOSTNAME.json </dev/null >/dev/null 2>&1 '".format(config_prefix))

    # kill middleware(s)
    print("killing middleware")
    system("parallel-ssh -t 0 -H '{}' 'killall java' ".format(mw_ips))

    # Move / rename the log files in MC to some place else, because it doesn't keep track of reps, or VC
    print("moving MW logs")
    system("ssh sgokula@sgokulaforaslvms4.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/2k-exp_{}_mw-1_log'".format(config_prefix))
    if num_mw == 2:
        system("ssh sgokula@sgokulaforaslvms5.westeurope.cloudapp.azure.com 'mv /home/sgokula/logs /home/sgokula/2k-exp_{}_mw-2_log'".format(config_prefix))

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