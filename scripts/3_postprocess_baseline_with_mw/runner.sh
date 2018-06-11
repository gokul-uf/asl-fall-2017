#!/bin/bash

echo "extracting info from one server MW logs"
python 3a_extract_tps_rtime_one_mw.py ../../logs/3a_one_mw_base_line/mw_log

echo "extracting info from one server MT logs"
python 3a_extract_tps_rtime_mt_one_mw.py ../../logs/3a_one_mw_base_line/mt_log

echo "plotting TPS, Latency from one server MW logs"
python 3a_plot_tps_rt_one_mw.py

echo "extracting info from two server MW logs"
python 3b_extract_tps_rtime_two_mw.py ../../logs/3b_two_mw_base_line/mw_log

echo "extracting info from two server MT logs"
python 3b_extract_tps_rtime_mt_two_mw.py ../../logs/3b_two_mw_base_line/mt_log

echo "plotting TPS, Latency from two server MW logs"
python 3b_plot_tps_rt_two_mw.py

