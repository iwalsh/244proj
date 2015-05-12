# hedera.py
#
# Reproducing the results of the Hedera paper.
#
# by Anh Truong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244, Spring 2015

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser

import sys
import os
from util.monitor import monitor_qlen
from util.helper import stdev


def cprint(s, color, cr=True):
    """Print in color
       s: string to print
       color: color to use"""
    if cr:
        print T.colored(s, color)
    else:
        print T.colored(s, color),


# Parse arguments

parser = ArgumentParser(description="Reproducing Hedera results")
parser.add_argument('--link_bw', '-B',
                    dest="link_bw",
                    type=float,
                    action="store",
                    help="Link bandwidth in Mb/s",
                    default=1000.0,
                    required=False)

parser.add_argument('--num_ports', '-k',
                    dest="k",
                    type=int,
                    action="store",
                    help="Number of ports per switch",
                    default=4,
                    required=False)

parser.add_argument('--delay',
                    dest="delay",
                    type=float,
                    help="Link delay in milliseconds",
                    default=60.0,
                    required=False)

parser.add_argument('--dir', '-d',
                    dest="dir",
                    action="store",
                    help="Directory to store outputs",
                    default="results",
                    required=True)

# parser.add_argument('--nflows',
#                     dest="nflows",
#                     action="store",
#                     type=int,
#                     help="Number of flows per host (for TCP)",
#                     required=True)

# parser.add_argument('--maxq',
#                     dest="maxq",
#                     action="store",
#                     help="Max buffer size of network interface in packets",
#                     default=1000)

# parser.add_argument('--cong',
#                     dest="cong",
#                     help="Congestion control algorithm to use",
#                     default="bic")

# parser.add_argument('--target',
#                     dest="target",
#                     help="Target utilisation",
#                     type=float,
#                     default=TARGET_UTIL_FRACTION)

# parser.add_argument('--iperf',
#                     dest="iperf",
#                     help="Path to custom iperf",
#                     required=True)

# Expt parameters
args = parser.parse_args()

if not k % 2 == 0:
    raise ValueError("k must be an even integer")

CUSTOM_IPERF_PATH = args.iperf
assert(os.path.exists(CUSTOM_IPERF_PATH))

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')


class FatTreeTopo(Topo):
    "Fat Tree Topology"

    # Example names for k=4
    def build(self, k, link_bw, delay):

        # Set up the (k/2)^2 core switches, c0 : c3
        core_switches = {}
        for i in xrange((k / 2) ** 2):
            name = 'c' + str(i)
            core_switches[name] = self.addSwitch(name)

        # Set up the k pods, each of k switches
        for pod in xrange(k):

            # First k/2 are aggregation switches, a0 : a1
            agg_switches = {}
            for agg in xrange(k / 2):
                name = 'a' + str(pod * (k / 2) + agg)
                agg_switch = self.addSwitch(name)
                agg_switches[name] = agg_switch

                # Each aggregation switch connects to k/2 core switches
                for c in xrange(k / 2):
                    core_switch = core_switches['c' + str(agg * (k / 2) + c)]
                    self.addLink(agg_switch, core_switch, bw=link_bw, delay=delay)

            # Second k/2 are edge switches, e0 : e1
            edge_switches = {}
            for edge in xrange(k / 2):
                name = 'e' + str(pod * (k / 2) + edge)
                edge_switch = self.addSwitch(name)
                edge_switches[name] = edge_switch

                # Each edge switch connects to k/2 agg switches (all in pod)
                for agg in xrange(k / 2):
                    agg_switch = agg_switches['a' + str(pod * (k / 2) + agg)]
                    self.addLink(edge_switch, agg_switch, bw=link_bw, delay=delay)

                # Each edge switch connects to k/2 end hosts
                for h in xrange(k / 2):
                    hostname = 'h' + str(pod * k + edge * (k / 2) + h)
                    host = self.addHost(hostname)
                    self.addLink(edge_switch, host, bw=link_bw, delay=delay)


def main(args):
    print 'Running Hedera testbed experiment with k=%d' % args.k

    start = time()
    # Reset to known state
    topo = FatTreeTopo(k=args.k, link_bw=args.link_bw, delay=args.delay)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    print 'All done in %fs!' % (time() - start)


if __name__ == '__main__':
    try:
        main(args)
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")
