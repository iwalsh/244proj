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

from fattree import FatTree

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser

import sys
import os


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

if not args.k % 2 == 0:
    raise ValueError("k must be an even integer")

# CUSTOM_IPERF_PATH = args.iperf
# assert(os.path.exists(CUSTOM_IPERF_PATH))

if not os.path.exists(args.dir):
    os.makedirs(args.dir)

lg.setLogLevel('info')


def main(args):
    print 'Running Hedera testbed experiment with k=%d' % args.k

    start = time()
    # Reset to known state
    topo = FatTree(k=args.k, link_bw=args.link_bw, delay=args.delay)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    CLI(net)
    net.pingAll()
    net.stop()

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
