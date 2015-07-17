# import datetime.datetime as datetime
import datetime as dt
import argparse
import os
import logging
import subprocess


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
    for d in get_child_dir(args.base_dir):
        if d == args.base_dir:
            continue
        parse_app_handle_pkt_in(os.path.join(d, 'notice.log'),
                                os.path.join(d, args.app_hdl_file))
        parse_controller_handle_pkt_in(os.path.join(d, 'notice.log'),
                                       os.path.join(d, args.ctrl_hdl_file))
        exec_plot(os.path.join(d, args.app_hdl_file),
                  os.path.join(d, args.ctrl_hdl_file),
                  os.path.join(d, args.output_plot),
                  args.open_plots)


def get_child_dir(dir):
    return [x[0] for x in os.walk(dir)]


# def parse_pkt_in():
#     with open(log_file) as f, open(pkt_in_count_file, 'w') as pkt_in:
#         prev_count = 0
#         for line in f:
#             if 'packet_in_count' in line:
#                 splitted = line.split()
#                 time = splitted[1].split('.')[0]
#                 secs_from_start = seconds_from_start(time)
#                 count_value = int(splitted[5].split(":")[1])
#                 calc_one_value = count_value - prev_count
#                 prev_count = count_value
#                 pkt_in.write('%d %d %d \n' % (secs_from_start, count_value,
#                                               calc_one_value))


def parse_app_handle_pkt_in(log_file, out_file):
    with open(log_file) as f, open(out_file, 'w') as out:
        for line in f:
            if 'app_handle_packet_in_mean' in line:
                splitted = line.split()
                time = splitted[1].split('.')[0]
                secs_from_start = seconds_from_start(time)
                value = int(splitted[5].split(":")[1])
                out.write('%d %d \n' % (secs_from_start, value))
    reset_time()


def parse_controller_handle_pkt_in(log_file, out_file):
    with open(log_file) as f, open(out_file, 'w') as out:
        for line in f:
            if 'controller_handle_packet_in_mean' in line:
                splitted = line.split()
                time = splitted[1].split('.')[0]
                secs_from_start = seconds_from_start(time)
                value = int(splitted[5].split(":")[1])
                out.write('%d %d \n' % (secs_from_start, value))
    reset_time()


def exec_plot(app_hdl_file, ctrl_hdl_file, output_plot, open_plots):
    cmd = ('gnuplot -e "output_plot=\'{output_plot}\'"' +
           ' -e "ctrl_hdl_file=\'{ctrl_hdl_file}\'"' +
           ' -e "app_hdl_file=\'{app_hdl_file}\'"' +
           ' scripts/plot_ls_stats.plg')
    formatted = cmd.format(app_hdl_file=app_hdl_file,
                           ctrl_hdl_file=ctrl_hdl_file,
                           output_plot=output_plot)
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
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--app-hdl-file', default='app_hdl_pkt_in.data')
    parser.add_argument('--ctrl-hdl-file', default='ctrl_hdl_pkt_in.data')
    parser.add_argument('--output-plot', default='plot.png')
    parser.add_argument('--open-plots', action='store_true')
    logging.basicConfig(level=logging.INFO)
    parse(parser.parse_args())


# gnuplot -e "output_plot='_rel/ls_runner/log/2015-07-14T17:12:25.774757/plot.png'" -e "ctrl_hdl_file='_rel/ls_runner/log/2015-07-14T17:12:25.774757/ctrl_hdl_pkt_in.data'" -e "app_hdl_file='_rel/ls_runner/log/2015-07-14T17:12:25.774757/app_hdl_pkt_in.data'" scripts/plot_ls_stats.plg     
