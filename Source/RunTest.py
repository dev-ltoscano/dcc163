# -*- coding: utf-8 -*-
import argparse
import os
import concurrent.futures

import Main

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--cm_dir", type=str, default="input_data/cenarios800", required=False)
arg_parser.add_argument("--cdis_dir", type=str, default="input_data/CDIS800", required=False)
arg_parser.add_argument("--out_dir", type=str, default="output_data/", required=False)
arg_parser.add_argument("--max_threads", type=int, default=1, required=False)

args = arg_parser.parse_args()

def run_in_thread(cm_file, cdis_file, out_dir):
    Main.main(cm_file, cdis_file, out_dir)

cm_file_list = []
cdis_file_list = []

# r=root, d=directories, f = files
for r, d, f in os.walk(args.cm_dir):
    for file in f:
        if (".xml" in file):
            cm_file_list.append(os.path.join(r, file))
            
for r, d, f in os.walk(args.cdis_dir):
    for file in f:
        if (".xml" in file):
            cdis_file_list.append(os.path.join(r, file))

with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_threads) as executor:
    for cm_file in cm_file_list:
        for cdis_file in cdis_file_list:
            executor.submit(run_in_thread, cm_file, cdis_file, args.out_dir)