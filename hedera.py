# hedera.py
#
# Reproducing the results of the Hedera paper.
#
# Running the POX controller:
# $ ~/pox/pox.py riplpox.riplpox --topo=ft,4 --routing=random --mode=reactive
#
# Running Mininet via this scriot (second terminal window)
# $ sudo python hedera.py traffic/stride1.json stride1_results
#
# by Anh Truong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244, Spring 2015

import os
import json

from time import time

from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from ripl.dctopo import FatTreeTopo

from argparse import ArgumentParser

IPERF_PATH = '/usr/bin/iperf'

HOST_NAMES = ('0_0_2', '0_0_3', '0_1_2', '0_1_3',
              '1_0_2', '1_0_3', '1_1_2', '1_1_3',
              '2_0_2', '2_0_3', '2_1_2', '2_1_3',
              '3_0_2', '3_0_3', '3_1_2', '3_1_3')

lg.setLogLevel('info')

parser = ArgumentParser(description="Reproducing Hedera results")
parser.add_argument('traffic', type=str,
                    help='Traffic JSON file created by traffic.py to use')
parser.add_argument('outdir', type=str,
                    help='Output directory for storing the results')
args = parser.parse_args()

if not os.path.isfile(args.traffic):
    raise Exception('Traffic file "%s" does not exist!' % args.traffic)


def get_receivers(traffic):
    """
    Return the indexes of the receiver hosts in [0:15]
    """
    receivers = []
    for sender in traffic:
        receivers += traffic[sender]
    return receivers


def start_receivers(net, traffic):
    """
    Start iperf on all of the receiver nodes.
    """
    receivers = get_receivers(traffic)
    for idx in receivers:
        host = net.get(HOST_NAMES[idx])
        host.popen("%s -s -p %d > %s/iperf_dst_%s.txt" % (IPERF_PATH, 5001,
                                                          args.outdir,
                                                          HOST_NAMES[idx]),
                   shell=True)


def start_senders(net, traffic):
    """
    Start iperf on all of the sender nodes
    """
    # Seconds to run iperf; keep this very high
    seconds = 3600

    for src_idx in traffic:
        src_name = HOST_NAMES[int(src_idx)]
        src = net.get(src_name)

        for dst_idx in traffic[src_idx]:
            dst_name = HOST_NAMES[dst_idx]
            dst = net.get(dst_name)

            src.popen("%s -c %s -p %s -t %d -i 1 -yc -Z bic > %s/%s" %
                      (IPERF_PATH, dst.IP(), 5001, seconds, args.outdir,
                       "%s_to_%s_iperf.txt" % (src_name, dst_name)),
                      shell=True)


def start_traffic(net):
    """
    Start long-lived iperf flows for all the (src, dst) pairs in traffic_file.
    """
    with open(args.traffic, 'r') as f:
        traffic = json.load(f)
    start_receivers(net, traffic)
    start_senders(net, traffic)


def main(args):
    print 'Running Hedera testbed experiments'

    start = time()
    topo = FatTreeTopo(k=4, speed=1.0)  # 1.0 Gbps links
    net = Mininet(topo=topo)
    net.addController(name='hederaController', controller=RemoteController,
                      ip='127.0.0.1', port=6633)
    net.start()
    dumpNodeConnections(net.hosts)
    CLI(net)

    print 'Generating the traffic pattern in "%s"...' % args.traffic
    start_traffic(net)

    # CLI(net)

    net.stop()

    print 'All done in %0.2fs!' % (time() - start)


if __name__ == '__main__':
    try:
        main(args)
    except:
        print "-" * 80
        print "Caught exception.  Cleaning up..."
        print "-" * 80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")
