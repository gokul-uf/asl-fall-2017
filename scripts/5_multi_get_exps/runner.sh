#!/bin/bash

echo "plotting average response time from memtier"
python plot_mt_avgs.py ../../logs/5_get_exp/mt_log/

echo "plotting percentile bar-graphs from memtier"
python plot_mt_percentiles.py ../../logs/5_get_exp/mt_log/

echo "plotting response-time histogram from middleware"
python plot_mw_histogram.py ../../logs/5_get_exp/raw_mw_log/

echo "plotting response-time histogram from middleware (without outliers)"
python plot_mw_hist_wo_outliers.py ../../logs/5_get_exp/raw_mw_log/

echo "plotting response-time histogram from memtier"
python plot_mt_histogram.py ../../logs/5_get_exp/mt_log/