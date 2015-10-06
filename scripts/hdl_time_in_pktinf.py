#!/usr/bin/env python

import sys, os, glob, logging, subprocess
import numpy as np

START_FROM_ROW = 16 # after 5 minutes
INCLUDE_ROWS = 20 # for 20 minutes

APP = 'app_handle_packet_in_mean.data'
CTRL = 'controller_handle_packet_in_mean.data'
PKTIN = 'packet_in_one.data'
COMBOUT = 'hdl_time_of_pktin.data'
OUT = 'out.data'

def path(dir, f):
  return os.path.join(dir, f)

def data_filename(dir):
  return os.path.basename(os.path.abspath(dir)) + ".data"

def plot_filename(dir):
  return os.path.basename(os.path.abspath(dir)) + ".png"

def metrics_files(dir):
  return [path(dir, f) for f in [PKTIN, APP, CTRL]]

def get_child_dirs(base_dir, pattern):
    return [d for d in glob.glob(os.path.join(base_dir, pattern + '*'))
            if os.path.isdir(d)]

def process_metrics_line(line):
  pktin,app,ctrl = line
  process = lambda s: s.split(' ')[1].strip()
  # pktin app ctrl
  return ' '.join([process(x) for x in [pktin, app, ctrl]])

def aggregate_metrics(child_dir):
  files = [open(f) for f in metrics_files(child_dir)]
  files_lines = [f.readlines() for f in files]
  zipped_lines = zip(*files_lines)
  with open(path(child_dir, COMBOUT), 'w') as f:
    f.write("#pktin app [micros] ctrl [micros]\n")
    for i, combined_line in enumerate(zipped_lines):
      # i == n-1 for the nth line
      if i < START_FROM_ROW - 1:
        continue
      elif i == START_FROM_ROW + INCLUDE_ROWS - 1:
        break
      pline = process_metrics_line(combined_line)
      f.write(pline + '\n')
  [f.close() for f in files]

def compute(child_dir, base_dir):
  data = np.loadtxt(path(child_dir, COMBOUT))
  avgs = np.mean(data, axis=0)
  stds = np.std(data, axis=0)
  with open(path(base_dir, data_filename(base_dir)), 'a') as out:
    for value,std in zip(avgs, stds):
      out.write("%.3f\t %.3f\t" % (value/1000, std/1000))
    out.write("\n")

def prepare_out(base_dir):
  with open(path(base_dir, data_filename(base_dir)), 'w') as out:
    out.write("# pktin\t pktin_std\t app\t app_std\t ctrl\t ctrl_std"\
              "# pkt in in thousands; times in milis\n")

def plot(base_dir):
  cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
         ' -e "data_file=\'{data_file}\'"' +
         ' scripts/plot_handle_time_of_pktin.plg')
  formatted = cmd.format(output_plot=path(base_dir, plot_filename(base_dir)),
                         data_file=path(base_dir, data_filename(base_dir)))
  logging.info('Running plot command %s' % formatted)
  result = subprocess.check_output([formatted],
                                   stderr=subprocess.STDOUT,
                                   shell=True)
  if result:
    logging.info("Plot cmd result %s" % result)

def main(base_dir):
  prepare_out(base_dir)
  for d in get_child_dirs(base_dir, "_2015"):
    aggregate_metrics(d)
    compute(d, base_dir)
  plot(base_dir)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  main(sys.argv[1])
  
  
