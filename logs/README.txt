This folder contains logs from client and middleware VMs for the different sections

The logs are subdivided into folders, each corresponding to a section in the report outline

Each folder has two sub-folders, mt_log and mw_log, these correspond to the memtier and middleware logs respectively (hence the prefix mt and mw). The mt_log folder, in addition to memtier logs, also contain output from dstat (prefix "dstat-") and results of ping tests (prefix "ping").

Each individual log is a JSON file making it easier to process downstream

Note that the Middleware logs are aggregated and the raw logs are not provided in the repository due to their large size. Please feel free to request them if needed.

The Middleware log's JSON consists of the following attributes
1. r_time - The response time
2. avg_q_len - The average queue length
3. mc_wait_time - Time MW waits for the memcached backends to reply to its request
4. quing_time - average time spent by request in the queue
5. tps - The throughput aggregated across the worker threads

Except in "tps" and "avg_q_len" above, the remaining attributes are averaged across worker threads in the middleware (or both middlewares in cases where there are two middlewares)

### Naming convention
I  try to maintain a consistent naming convention across the experiments but there might be slight deviations. But overall, the name of a log file will tell exactly what the experiment was and what the config was.
Naming conventions are like <attribute_1>-<value_1>_<attribute_2>-<value_2>_....

The usual naming convention for middleware logs is <exp_name>_<work_load>_c-<num_virtual_clients>_t-<num_worker_threads>_rep_<which_repetition>... .json

Memtier logs start with "mt_" instead of <exp_name>, they also end with "foraslvms[1 / 2 / 3]" corresponding to the hostname of the memtier VM in cases where we use more than one load-generating VM. The rest of the convention is similar to the middleware convention.

In case, the above convention doesn't match, please use the following table to decipher the name

1. c-<V>   == there are "V" virtual clients per thread in this configuration
2. t-<T>   == there are "T" worker thread per middleware in this configuration
3. rep-<R> == This is the "R"th repition of this experiment
4. "r-o" / "w-o" / "r-w" == the workload is read-only / write-only / 50-50 read-write
5. s-<B>   == If B is True, sharding is enabled in the middelware, disabled if False
5. g-<G>   == Used in multi-get experiments, there are G keys in one multi-GET request
6. mw-<MW> == Corresponds the first or second middleware in multi-middleware experiments

