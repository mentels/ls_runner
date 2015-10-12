#!/usr/bin/env python

import sys, os, glob, logging, subprocess, re
import numpy as np

START_FROM_ROW = 16 # after 15 minutes
INCLUDE_ROWS = 20 # for 20 minutes

APP = 'app_handle_packet_in_mean.data'
CTRL = 'controller_handle_packet_in_mean.data'
PKTIN = 'packet_in_one.data'
COMBOUT = 'hdl_time_of_pktin.data'

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

def get_switches_and_hosts_from_dir(child_dir):
   p = re.compile(r'.*-c:(?P<hosts>\d+).*-sw:(?P<switches>\d+).*')
   m = p.search(child_dir)
   return (int(m.group('hosts')), int(m.group('switches')))

def compute(child_dir, base_dir, acc):
  hosts,switches = get_switches_and_hosts_from_dir(child_dir)
  data = np.loadtxt(path(child_dir, COMBOUT))
  avgs = np.mean(data, axis=0)
  stds = np.std(data, axis=0)
  zipped = zip(avgs, stds)
  zipped.append((switches, hosts))
  acc.append(zipped)
  return acc

def store_data(base_dir, avgs_with_stds_list):
  with open(path(base_dir, data_filename(base_dir)), 'a') as out:
    for avgs_with_stds in avgs_with_stds_list:
      store_row_in_file(out, avgs_with_stds)

def store_row_in_file(out, avgs_with_stds):
  for i,(value,std) in enumerate(avgs_with_stds):
    if i==3:
      switches_and_hosts = (value,std)
      out.write("%d,%d\n" % switches_and_hosts)
    else:
      out.write("%.3f,%.3f," % (value/1000, std/1000))  

def prepare_out(base_dir):
  with open(path(base_dir, data_filename(base_dir)), 'w') as out:
    out.write("pktin,pktin_std,app,app_std,ctrl,ctrl_std,switches,hosts\n")

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

def sort_by_pktin(avgs_with_stds_list):
  avgs_with_stds_list.sort(key = lambda t: t[0][0])
  return avgs_with_stds_list

def main(base_dir):
  prepare_out(base_dir)
  acc = []
  for d in get_child_dirs(base_dir, "*2015"):
    aggregate_metrics(d)
    acc = compute(d, base_dir, acc)
  store_data(base_dir, sort_by_pktin(acc))
  plot(base_dir)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  main(sys.argv[1])
  
  
