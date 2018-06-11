# Network of Queues model for two middleware
pkg load queueing


# plug-in the following, times in milliseconds

nw_lat_time = 8; # lat_client - lat_mw
nt_service_time = 0.001;  
wt_service_time = 3;

m = 8;  # Number of threads
N = 64; # Num VC here
Z = 0;  # Thinking time is zero

nw_1 = qnmknode("-/g/inf", nw_lat_time); # MT to MW ID_1
nt_1 = qnmknode("m/m/m-fcfs", nt_service_time); # Net Thread 1 ID_2 
nt_2 = qnmknode("m/m/m-fcfs", nt_service_time); # Net Thread 2 ID_3

wt_1 = qnmknode("m/m/m-fcfs", wt_service_time, m); # Worker thread + MC in MW_1 ID_4
wt_2 = qnmknode("m/m/m-fcfs", wt_service_time, m); # Worker thread + MC in MW_2 ID_5
nw_2 = qnmknode("-/g/inf", nw_lat_time); # MW to MT ID_6

QQ = { nw_1,
       nt_1,
       nt_2,
       wt_1,
       wt_2,
       nw_2 };

P = zeros(6, 6);
P(1, 2) = 0.5;
P(1, 3) = 0.5;
P(2, 4) = 1;
P(3, 5) = 1;
P(4, 6) = 1;
P(5, 6) = 1;
P(6, 1) = 1;

V = qncsvisits(P);

[U R Q X] = qnsolve("closed", N, QQ, V, Z)