# hedera.py
#
# Reproducing the results of the Hedera paper.
#
# Running the POX controller:
# $ ~/pox/pox.py controllers.riplpox --topo=ft,4 --routing=hashed --mode=reactive
#
# Running Mininet via this script (second terminal window)
# $ sudo python hedera.py ecmp traffic/stride1.json
#
# ^ The 'ecmp' parameter here does NOT actually control which scheduling is
# used - that is determined by the POX command. It just tells this script how
# to label the results when we persist them.
#
# by Anh Truong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244, Spring 2015

import os
import json

from time import time, sleep
from math import sqrt

from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from ripllib.dctopo import FatTreeTopo

from argparse import ArgumentParser

# Number of seconds to sample the flows
N_SAMPLES = 10

# We must skip at least the first sample to establish a baseline bytes_recvd
SAMPLES_TO_SKIP = 1

IPERF_PATH = '/usr/bin/iperf'
IPERF_PORT = 5001
IPERF_PORT_BASE = 5001
IPERF_SECONDS = 3600

OUTDIR = 'results/'

popens = {}
popen_receivers = {}

HOST_NAMES = ('0_0_2', '0_0_3', '0_1_2', '0_1_3',
              '1_0_2', '1_0_3', '1_1_2', '1_1_3',
              '2_0_2', '2_0_3', '2_1_2', '2_1_3',
              '3_0_2', '3_0_3', '3_1_2', '3_1_3')

lg.setLogLevel('info')

parser = ArgumentParser(description='Reproducing Hedera results')
parser.add_argument('algorithm', type=str, choices=('ecmp', 'gff'),
                    help='Routing algorithm for saving results')
parser.add_argument('traffic', type=str,
                    help='Traffic JSON file created by traffic.py to use')
args = parser.parse_args()

if not os.path.isfile(args.traffic):
    raise Exception('Traffic file "%s" does not exist!' % args.traffic)

if not os.path.isdir(OUTDIR):
    raise Exception('Output directory "%s" does not exist!' % OUTDIR)


def start_traffic(net):
    """
    Start long-lived iperf flows for all the (src, dst) pairs in traffic_file.
    """
    with open(args.traffic, 'r') as f:
        traffic = json.load(f)

    # Start every flow on its own port
    port_count = 0
    for src_idx in traffic:
        src_name = HOST_NAMES[int(src_idx)]
        src = net.get(src_name)

        for dst_idx in traffic[src_idx]:
            dst_name = HOST_NAMES[dst_idx]
            dst = net.get(dst_name)

            port = IPERF_PORT_BASE + port_count
            server = '%s -s -p %s &' % (IPERF_PATH, port)
            client = '%s -c %s -p %s -t %d &' % (IPERF_PATH,
                                                 dst.IP('%s-eth0' % dst_name),
                                                 port, IPERF_SECONDS)
            dst.cmd(server)
            src.cmd(client)
            print 'Started iperf flow %s (%s) -> %s (%s) on port %d' %\
                  (src_name, src.IP('%s-eth0' % src_name), dst_name,
                   dst.IP('%s-eth0' % dst_name), port)
            port_count += 1


def avg(lst):
    return float(sum(lst)) / len(lst)


def variance(lst):
    mean = avg(lst)
    diffs_sqrd = []
    for val in lst:
        diffs_sqrd.append((val - mean) ** 2)
    return avg(diffs_sqrd)


def bytes_to_throughputs(rxbytes, durations):
    """
    Convert samples of cumulative bytes received to bytes per second.
    If rxbytes has N_SAMPLES, then throughputs has N_SAMPLES - 1.
    """
    throughputs = {}
    for name in HOST_NAMES:
        throughputs[name] = []

    for name in rxbytes:
        for i, sample in enumerate(rxbytes[name]):
            if i:  # i > 0
                throughput = (sample - rxbytes[name][i - 1]) / durations[i]
                throughputs[name].append(throughput)

    return throughputs


def sample_rxbytes(net, rxbytes):
    """
    For each host, parse received bytes from /proc/net/dev, which has the
    format:

    Inter-|   Receive                                             |  Transmit
     face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
    lo:       0       0    0    0    0     0          0         0        0       0    0    0    0     0       0          0
3_1_3-eth0: 33714765732 1133072    0    0    0     0          0         0 25308223734 1110457    0    0    0     0       0          0
    """
    for name in HOST_NAMES:
        host = net.get(name)
        iface = '%s-eth0:' % name
        bytes = None

        res = host.cmd('cat /proc/net/dev')
        lines = res.split('\n')
        for line in lines:
            if iface in line:
                bytes = int(line.split()[1])
                rxbytes[name].append(bytes)
                break

        if bytes is None:
            lg.error('Couldn\'t parse rxbytes for host %s!\n' % name)


def aggregate_statistics(rxbytes, sample_durations):
    """
    Return the average throughput and variance summed over each host, in
    bytes/sec
    """
    throughputs = bytes_to_throughputs(rxbytes, sample_durations)

    agg_throughput = 0.0
    agg_variance = 0.0

    for name in throughputs:
        agg_throughput += avg(throughputs[name])
        agg_variance += variance(throughputs[name])

    return (agg_throughput, agg_variance)


def save_results(mean_gbps, stddev_gbps):
    """
    Save results as json to OUTDIR/<traffic_filename>.json
    (e.g. results/stride1.json).
    Won't clobber existing results for other algorithms, if present.
    """
    filename = args.traffic.split('/')[-1]
    outfile = OUTDIR + filename

    if os.path.isfile(outfile):
        # Append to existing json; don't clobber
        with open(outfile, 'r') as f:
            results = json.load(f)

        os.remove(outfile)
    else:
        results = {}

    results['%s_mean_gbps' % args.algorithm] = mean_gbps
    results['%s_stddev_gbps' % args.algorithm] = stddev_gbps

    with open(outfile, 'w') as f:
        json.dump(results, f)

    print 'Results saved to %s!' % outfile


def main(args):
    print 'Running Hedera testbed experiments'

    # Shut down iperf processes
    os.system('killall -9 ' + IPERF_PATH)

    start = time()
    topo = FatTreeTopo(k=4, speed=1.0)  # 1.0 Gbps links
    net = Mininet(topo=topo)
    net.addController(name='hederaController', controller=RemoteController,
                      ip='127.0.0.1', port=6633)
    net.start()
    dumpNodeConnections(net.hosts)

    sleep(5)

    # CLI(net)

    print 'Generating the traffic pattern in "%s"...' % args.traffic
    start_traffic(net)

    # Sample the cumulative # of bytes received for each host, every second.
    # The diff between adjacent samples gives us throughput for that second.
    rxbytes = {}
    sample_durations = []
    for name in HOST_NAMES:
        rxbytes[name] = []

    now = time()
    for i in xrange(N_SAMPLES):
        print 'Taking sample %d of %d...' % (i, N_SAMPLES)
        sample_durations.append(time() - now)
        now = time()
        sample_rxbytes(net, rxbytes)
        sleep(1.0)

    (agg_mean, agg_var) = aggregate_statistics(rxbytes, sample_durations)
    agg_stddev = sqrt(agg_var)
    mean_gbps = agg_mean / (2 ** 30) * 8
    stddev_gbps = agg_stddev / (2 ** 30) * 8
    print 'Total average throughput: %f bytes/sec (%f Gbps)' %\
          (agg_mean, mean_gbps)
    print 'Standard deviation: %f bytes/sec (%f Gbps)' %\
          (agg_stddev, stddev_gbps)

    save_results(mean_gbps, stddev_gbps)

    # CLI(net)

    # Shut down iperf processes
    os.system('killall -9 ' + IPERF_PATH)

    net.stop()

    print 'All done in %0.2fs!' % (time() - start)


if __name__ == '__main__':
    try:
        main(args)
    except:
        print '-' * 80
        print 'Caught exception.  Cleaning up...'
        print '-' * 80
        import traceback
        traceback.print_exc()
        os.system('killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c')
