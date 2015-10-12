# import datetime.datetime as datetime
import datetime as dt
import argparse
import os
import logging
import subprocess
import glob
import re


def seconds_from_start(raw_time):
    t = dt.datetime.strptime(raw_time, "%H:%M:%S")
    if hasattr(seconds_from_start, "init_datetime"):
        diff = t - seconds_from_start.init_datetime
        return diff.total_seconds()
    else:
        seconds_from_start.init_datetime = t
        return 0


def reset_time():
    if hasattr(seconds_from_start, "init_datetime"):
        delattr(seconds_from_start, "init_datetime")


def parse(args):
    chd = get_child_dirs(args.base_dir, args.log_dir_pattern)
    logging.info('Found log dirs: %s' % chd)
    for d in get_child_dirs(args.base_dir, args.log_dir_pattern):
        process_histogram_metrics(d, args.open_plots)
        process_counter_metrics(d, args.open_plots, args.cnt_div)

def master_plot_filename(child_dir):
  p = re.compile(r'.*-c:(?P<hosts>\d+).*-sw:(?P<switches>\d+).*-m:(?P<mode>(proc_per_switch|regular)).*-sch:(?P<schedulers>\d+)')
  m = p.search(child_dir)
  mode = m.group('mode')
  if m.group('mode') == 'proc_per_switch':
    mode = 'ppsw'
  return '_240h_%s_%ssch_%ssw_%shpsw.png' % (mode, m.group('schedulers'),
                                             m.group('switches'), m.group('hosts'))


def process_histogram_metrics(d, open_plots):
    metrics = ['app_handle_packet_in_mean', 'controller_handle_packet_in_mean',
               'fwd_table_size_mean']
    for m in metrics:
        parse_metric(m, os.path.join(d, 'notice.log'),
                     os.path.join(d, m + '.data'), 1)
    exec_packet_in_handle_plot(os.path.join(d, metrics[0] + '.data'),
                               os.path.join(d, metrics[1] + '.data'),
                               os.path.basename(d),
                               open_plots,
                               os.path.join(d, 'packet_in_handle.png'))
    exec_packet_in_handle_plot(os.path.join(d, metrics[0] + '.data'),
                               os.path.join(d, metrics[1] + '.data'),
                               " ",
                               open_plots,
                               os.path.join(d, '..', master_plot_filename(d)))
    exec_fwd_table_size_plot(os.path.join(d, metrics[2] + '.data'),
                             os.path.basename(d),
                             open_plots,
                             os.path.join(d, 'fwd_table_size.png'))


def process_counter_metrics(d, open_plots, divide_by):
    metrics = ['packet_in_one', 'packet_out_one', 'flow_mod_one']
    for m in metrics:
        parse_metric(m, os.path.join(d, 'notice.log'),
                     os.path.join(d, m + '.data'), divide_by)
    exec_counters_plot(os.path.join(d, metrics[0] + '.data'),
                       os.path.join(d, metrics[1] + '.data'),
                       os.path.join(d, metrics[2] + '.data'),
                       os.path.basename(d),
                       open_plots,
                       os.path.join(d, 'counters.png'))


def get_child_dirs(base_dir, pattern):
    return [d for d in glob.glob(os.path.join(base_dir, pattern + '*'))
            if os.path.isdir(d)]


def parse_metric(metric_string, log_file, out_file, divide_by):
    with open(log_file) as f, open(out_file, 'w') as out:
        for line in f:
            if metric_string in line:
                splitted = line.split()
                time = splitted[1].split('.')[0]
                secs_from_start = seconds_from_start(time)
                value = int(splitted[5].split(":")[1])
                out.write('%d %d \n' % (secs_from_start, value/int(divide_by)))
    reset_time()


def exec_packet_in_handle_plot(app_hdl_file, ctrl_hdl_file, plot_title,
                               open_plots, output_plot):
    cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
           ' -e "ctrl_hdl_file=\'{ctrl_hdl_file}\'"' +
           ' -e "app_hdl_file=\'{app_hdl_file}\'"' +
           ' -e "plot_title=\'{plot_title}\'"' +
           ' scripts/plot_handle_packet_in.plg')
    formatted = cmd.format(app_hdl_file=app_hdl_file,
                           ctrl_hdl_file=ctrl_hdl_file,
                           output_plot=output_plot,
                           plot_title=plot_title)
    logging.info('Running plot command %s' % formatted)
    result = subprocess.check_output([formatted],
                                     stderr=subprocess.STDOUT,
                                     shell=True)
    if result:
        logging.info("Plot cmd result %s" % result)
    if open_plots:
        subprocess.call(['ristretto %s &' % output_plot], shell=True)


def exec_counters_plot(packet_inf, packet_outf, flow_modf, plot_title,
                       open_plots, output_plot):
    cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
           ' -e "packet_inf=\'{packet_inf}\'"' +
           ' -e "packet_outf=\'{packet_outf}\'"' +
           ' -e "flow_modf=\'{flow_modf}\'"' +
           ' -e "plot_title=\'{plot_title}\'"' +
           ' scripts/plot_counters.plg')
    formatted = cmd.format(packet_inf=packet_inf,
                           packet_outf=packet_outf,
                           flow_modf=flow_modf,
                           output_plot=output_plot,
                           plot_title=plot_title)
    logging.info('Running plot command %s' % formatted)
    result = subprocess.check_output([formatted],
                                     stderr=subprocess.STDOUT,
                                     shell=True)
    if result:
        logging.info("Plot cmd result %s" % result)
    if open_plots:
        subprocess.call(['ristretto %s &' % output_plot], shell=True)


def exec_fwd_table_size_plot(fwd_table_sizef, plot_title, open_plots,
                             output_plot):
    cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
           ' -e "fwd_table_sizef=\'{fwd_table_sizef}\'"' +
           ' -e "plot_title=\'{plot_title}\'"' +
           ' scripts/plot_fwd_table_size.plg')
    formatted = cmd.format(fwd_table_sizef=fwd_table_sizef,
                           output_plot=output_plot,
                           plot_title=plot_title)
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
    parser.add_argument('--log-dir-pattern', default='')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--output-plot', default='plot.png')
    parser.add_argument('--open-plots', action='store_true')
    parser.add_argument('--cnt-div', default=1)
    logging.basicConfig(level=logging.INFO)
    parse(parser.parse_args())
