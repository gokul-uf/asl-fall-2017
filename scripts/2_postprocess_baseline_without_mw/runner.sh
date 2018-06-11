#!/bin/bash
echo "extracting one mc baseline info"
python 2a_extract_tps_rtime_one_mc_baseline.py ../../logs/2a_one_server_base_line_log

echo "plotting one mc baseline values"
python 2a_plot_tps_rtime_one_mc_baseline.py

echo "extracting two mc baseline info"
python 2b_extract_tps_rtime_two_mc_baseline.py ../../logs/2b_two_server_base_line_log

echo "plotting two mc baseline values"
python 2b_plot_tps_rtime_two_mc_baseline.py

echo "plotting interactive law plots"
python 2_plot_interactive.py