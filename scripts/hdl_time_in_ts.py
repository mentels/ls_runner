#!/usr/bin/env python

import sys, glob, logging, subprocess, re
import os.path as path
import numpy as np

COMBOUT = 'hdl_time_of_pktin.data'

def dir_sch(sch):
  return '_240h_ppsw_%dsch' % sch

def plot(base_dir):
  cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
         ' -e "sch2_file=\'{sch2_file}\'"' +
         ' -e "sch4_file=\'{sch4_file}\'"' +
         ' -e "sch8_file=\'{sch8_file}\'"' +
         ' scripts/plot_handle_time_of_test_scenario.plg')
  formatted = cmd.format(output_plot=path.join(base_dir, '_240h_ppsw.png'),
                         sch2_file=path.join(base_dir, dir_sch(2), dir_sch(2)+'.data'),
                         sch4_file=path.join(base_dir, dir_sch(4), dir_sch(4)+'.data'),
                         sch8_file=path.join(base_dir, dir_sch(8), dir_sch(8)+'.data')
  )
  logging.info('Running plot command %s' % formatted)
  result = subprocess.check_output([formatted],
                                   stderr=subprocess.STDOUT,
                                   shell=True)
  if result:
    logging.info("Plot cmd result %s" % result)

def main(base_dir):
  plot(base_dir)


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  main(sys.argv[1])
