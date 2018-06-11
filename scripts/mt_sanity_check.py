from __future__ import print_function
from __future__ import division

import json
import os
import sys
from glob import glob

if __name__ == "__main__":
    miss_count = 0
    folder = os.path.abspath(sys.argv[1])
    files = glob("{}/*.json".format(folder))
    print("Found {} files".format(len(files)))
    for filename in files:
    	try:	
	        js = json.load(open(os.path.abspath(filename)))
	        if  js["ALL STATS"]["Gets"]["Misses/sec"] != 0.0:
	            print("WARN: Get Misses in {}".format(filename))
	        
	        if  js["ALL STATS"]["Sets"]["Misses/sec"] != 0.0:
	        	print("WARN: Set Misses in {}".format(filename))
                        miss_count += 1
    	except:
    		print("ERROR Parsing: {}".format(filename))

    if miss_count == 0:
        print("SUCCESS: No GET or SET Misses!")
