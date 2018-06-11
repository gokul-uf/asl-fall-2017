#!/bin/bash

LOG_BASE_DIR=/home/gokul/.eclipse-workspace/asl-fall17-project/logs/

## Section 2
echo "Processing Sec. 2: baselines without middleware"
echo "	sanity checking MT logs"
python mt_sanity_check.py $LOG_BASE_DIR/2a_one_server_base_line_log
python mt_sanity_check.py $LOG_BASE_DIR/2b_two_server_base_line_log

echo "	running postprocessor"
cd 2_postprocess_baseline_without_mw
./runner.sh
cd ..


# Section 3
echo "Processing Sec. 3: baselines with middleware"
echo "	sanity checking MT logs"
python mt_sanity_check.py $LOG_BASE_DIR/3a_one_mw_base_line/mt_log
python mt_sanity_check.py $LOG_BASE_DIR/3b_two_mw_base_line/mt_log

echo "	sanity checking MW logs"
python raw_mw_sanity_check.py $LOG_BASE_DIR/3a_one_mw_base_line/raw_mw_log
python raw_mw_sanity_check.py $LOG_BASE_DIR/3b_two_mw_base_line/raw_mw_log

echo "not processing MW logs"
# python mw_folder_postprocessor.py $LOG_BASE_DIR/3a_one_mw_base_line/raw_mw_log
# python mw_folder_postprocessor.py $LOG_BASE_DIR/3b_two_mw_base_line/raw_mw_log

# echo "	move processed MW logs"
# mv $LOG_BASE_DIR/3a_one_mw_base_line/raw_mw_log/*.json $LOG_BASE_DIR/3a_one_mw_base_line/mw_log
# mv $LOG_BASE_DIR/3b_two_mw_base_line/raw_mw_log/*.json $LOG_BASE_DIR/3b_two_mw_base_line/mw_log

echo " running postprocessor"
cd 3_postprocess_baseline_with_mw 
./runner.sh
cd ..


## Section 4
echo "Processing Sec. 4: SET Throughput"
echo "	sanity checking MT logs"
python mt_sanity_check.py $LOG_BASE_DIR/4_set_tps_log/mt_log

echo "	sanity checking MW logs"
python raw_mw_sanity_check.py $LOG_BASE_DIR/4_set_tps_log/raw_mw_log

# echo "	processing MW logs"
# python mw_folder_postprocessor.py $LOG_BASE_DIR/4_set_tps_log/raw_mw_log

# echo "	move processed MW logs"
# mv $LOG_BASE_DIR/4_set_tps_log/raw_mw_log/*.json $LOG_BASE_DIR/4_set_tps_log/mw_log

echo "	running postprocessor"
cd 4_postprocess_sets_tps
./runner.sh
cd ..


## Section 5
echo "Processing Sec. 5: GET and Multi-GET"
echo "	sanity checking MT logs"
python mt_sanity_check.py $LOG_BASE_DIR/5_get_exp/mt_log

echo "	sanity checking MW logs"
python raw_mw_sanity_check.py $LOG_BASE_DIR/5_get_exp/raw_mw_log

echo "	running postprocessor"
cd 5_multi_get_exps
./runner.sh
cd ..


# ## Section 6
echo "Processing Sec. 6: 2K Analysis"
echo "	sanity checking MT logs"
python mt_sanity_check.py $LOG_BASE_DIR/6_2k_exp_log/mt_log
echo "	sanity checking MW logs"
python raw_mw_sanity_check.py $LOG_BASE_DIR/6_2k_exp_log/raw_mw_log
# echo "	processing MW logs"
# python mw_folder_postprocessor.py $LOG_BASE_DIR/6_2k_exp_log/raw_mw_log
# echo "moving the MW summaries"
# mv $LOG_BASE_DIR/6_2k_exp_log/raw_mw_log/*.json $LOG_BASE_DIR/6_2k_exp_log/mw_log
echo "	running postprocessor"
cd 6_postprocess_2k_exp
./runner.sh
cd ..
