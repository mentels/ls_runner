# import datetime.datetime as datetime
import datetime as dt
import argparse
import os
import logging
import subprocess
import glob
import numpy as np
from StringIO import StringIO
import re

# Running:
# 1) parse_ls_logs.py that produces data for the metrics
# 2) 
# python scripts/parse_ls_logs2.py --base-dir ~/Dropbox/MGR/testy/logs_2015_07_31-mh:2-sw:2-it:1000-m:proc_per_switch/ --schedulers 8


def parse(args):
    plotDataFile = os.path.join(args.base_dir, 'sch:' + args.schedulers + '.data')
    plotTitle = plotDataFile
    with open(plotDataFile, 'w') as f:
        for logDir in get_child_dirs(args.base_dir, args.schedulers):
            if logDir == args.base_dir or os.path.basename(logDir).startswith('_'):
                continue
            containersNum = get_mininet_containers_number(logDir)
            avgs = process_histogram_metrics(logDir)
            f.write('%s %s %s\n' % (containersNum, avgs[0], avgs[1]))
    exec_packet_in_handle_plot(plotDataFile, plotTitle, args.open_plots)
    

def get_mininet_containers_number(logDir):
	m = re.search(".*c:(?P<MNC>\\d+).*", logDir)
	return m.group('MNC') 


def process_histogram_metrics(logDir):
    metrics = ['app_handle_packet_in_mean', 'controller_handle_packet_in_mean']
    times = []
    for m in metrics:
    	filename = os.path.join(logDir, m + '.data')
    	data = np.loadtxt(filename)
        times.append(data.mean(axis=0)[1])
    return times


def get_child_dirs(base_dir, schedulers):
    return [d for d in glob.glob(os.path.join(base_dir, '*sch:' + schedulers))
            if os.path.isdir(d)]



def exec_packet_in_handle_plot(dataFile, title, open_plots):
    output_plot=dataFile.split('.')[0] + '.png'
    cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
           ' -e "data=\'{data}\'"' +
           ' -e "plot_title=\'{plot_title}\'"' +
           ' scripts/plot_handle_packet_in2.plg')
    formatted = cmd.format(data=dataFile,
                           output_plot=output_plot,
                           plot_title=title)
    logging.info('Running plot command %s' % formatted)
    result = subprocess.check_output([formatted],
                                     stderr=subprocess.STDOUT,
                                     shell=True)
    if result:
        logging.info("Plot cmd result %s" % result)
    if open_plots:
        subprocess.call(['ristretto %s &' % output_plot], shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Loom Switch Logs')
    parser.add_argument('--base-dir', default='_rel/ls_runner/log')
    parser.add_argument('--schedulers', default='')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--output-plot', default='plot.png')
    parser.add_argument('--open-plots', action='store_true')
    logging.basicConfig(level=logging.INFO)
    parse(parser.parse_args())
