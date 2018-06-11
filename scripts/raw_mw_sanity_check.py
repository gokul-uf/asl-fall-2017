from __future__ import print_function
from __future__ import division

import json
import os
import sys
from glob import glob

# checks that there are no errors and info files are not empty

if __name__ == "__main__":
    log_dir = os.path.abspath(sys.argv[1])
    print("Sanity Checking MW log folder: \n{}".format(log_dir))
    folders = glob("{}/*".format(log_dir))
    folders = [os.path.abspath(folder) for folder in folders if os.path.isdir(folder)]

    for folder in folders:
        info_files = glob("{}/*.info".format(folder))
        info_files = [f for f in info_files if "_id-" in f]

        error_files = glob("{}/*.error".format(folder))

        for info_file in info_files:
            if os.path.getsize(info_file) == 0:
                print("WARN: Info File {} is empty".format(info_file))

        for error_file in error_files:
            if os.path.getsize(error_file) != 0:
                print("WARN: Error File {} is not empty".format(error_file))
    print("Checked {} folders, LGTM".format(len(folders)))

