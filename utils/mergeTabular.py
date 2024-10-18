#!/usr/bin/env python3

import pandas as pd
import sys, os

"""
Run once to generate merged tabular data
Make sure merged csv is not present before generation!

RANDOM SAMPLING!!! --> Not suitable for time-series analysis

-s: Source directory with all the csv files
-t: Target file path which is the merged csv
-sc: Sample Count for choosing the sample size for each csv
"""

# If you want you can select sampleCount by using pngCount.sh!

if(sys.argv[1] == "-s" and sys.argv[3] == "-t", sys.argv[5] == "-sc"):
    srcDir = sys.argv[2]
    mergedPath = sys.argv[4]    
    sampleCount = int(sys.argv[6])
else:
    print("Wrong format! Exiting...")
    sys.exit(0)

for file in os.listdir(srcDir):
    df = pd.read_csv(f"{srcDir}/{file}")
    df.Filename = file[:-4] + "/" + df.Filename
    df = df.sample(n = sampleCount)
    if(not os.path.exists(mergedPath)):
        df.to_csv(mergedPath, index = False, header = True)
    else:
        df.to_csv(mergedPath, mode = "a", index = False, header = False)

print(f"Merged CSV created at {mergedPath}!")
