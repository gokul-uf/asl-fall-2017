#!/bin/bash
python 4_extract_info.py ../../logs/4_set_tps_log/mw_log
python 4_plot_tps.py
python 4_extract_mt_info.py ../../logs/4_set_tps_log/mt_log/