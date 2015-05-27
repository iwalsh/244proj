# traffic.py
#
# Utilities to create the traffic matrices used in our experiments with the
# Hedera controller. Constructs and prints a json representation of the dst
# hosts for each sender.
#
# Example usage:
#   $ python traffic.py stride1 > traffic/stride1.json
#
# by Anh Truong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244 Lab 3, Spring 2015

import random
import json
from argparse import ArgumentParser

N_HOSTS = 16
N_HOSTS_PER_POD = 4
N_PODS = 4

parser = ArgumentParser(description="Generate traffic matrix")
parser.add_argument('pattern', type=str)


def pod_idx(host_idx):
    return host_idx / N_PODS


# e.g. [0, 1, 2, 3] for pod_idx = 0
def hosts_in_pod(pod_idx):
    start = pod_idx * N_HOSTS_PER_POD
    return range(start, start + N_HOSTS_PER_POD)


def other_host_in_pod(host):
    pod = hosts_in_pod(pod_idx(host))
    pod.remove(host)
    return random.choice(pod)


def other_host_outside_pod(host):
    hosts = range(N_HOSTS)
    pod = hosts_in_pod(pod_idx(host))
    for h in pod:
        hosts.remove(h)
    return random.choice(hosts)


def traffic_stride1():
    return traffic_stride(1)


def traffic_stride2():
    return traffic_stride(2)


def traffic_stride4():
    return traffic_stride(4)


def traffic_stride8():
    return traffic_stride(8)


def traffic_stride(i):
    """
    A host with index x sends to the host with index (x + i) mod N_HOSTS
    """
    traffic = {}
    for x in range(N_HOSTS):
        traffic[str(x)] = [(x + i) % N_HOSTS]
    return traffic


def traffic_stag0203():
    return traffic_staggered(0.2, 0.3)


def traffic_stag0503():
    return traffic_staggered(0.5, 0.3)


def traffic_staggered(edge_p, pod_p):
    """
    A host sends to another host in the same edge switch with probability
    edge_p, and to its same pod with probability pod_p, and to the rest of
    the network with probability 1 - edge_p - pod_p.

    ^ Somewhat ambiguously worded, but every host sends to exactly 1 other
    host: not 0, and not 3.
    """
    traffic = {}
    for x in range(N_HOSTS):
        traffic[str(x)] = []

        rand = random.random()

        if rand <= edge_p:
            # Send to host on same edge switch w/ prob edge_p
            if x % 2 == 0:
                dst = x + 1
            else:
                dst = x - 1
            traffic[str(x)].append(dst)
        elif rand <= (edge_p + pod_p):
            # Send to host in same pod with probability pod_p
            traffic[str(x)].append(other_host_in_pod(x))
        else:
            # Send to non-pod host with prob (1 - edge_p - pod_p)
            traffic[str(x)].append(other_host_outside_pod(x))

    return traffic


def traffic_random():
    """
    A host sends to any other host in the network with uniform probability.
    """
    traffic = {}
    for x in range(N_HOSTS):
        hosts = range(N_HOSTS)
        hosts.remove(x)
        traffic[str(x)] = [random.choice(hosts)]
    return traffic


def traffic_bijective():
    """
    There is a bijection between senders and recievers, so that each host is
    the dst of exactly one flow.
    """
    traffic = {}
    dsts = range(N_HOSTS)
    for x in range(N_HOSTS):
        choice = random.choice(dsts)
        while choice == x:
            # A host shouldn't send to itself; might endlessly loop but meh, Ctrl+C
            choice = random.choice(dsts)
        traffic[str(x)] = [choice]
        dsts.remove(choice)
    return traffic


def traffic_hotspot():
    """
    All hosts try to send to the same dst host, chosen at random.
    """
    dst = random.choice(range(N_HOSTS))
    traffic = {}
    for x in range(N_HOSTS):
        if x == dst:
            pass
        else:
            traffic[str(x)] = [dst]
    return traffic


TRAFFIC = {'stride1': traffic_stride1,
           'stride2': traffic_stride2,
           'stride4': traffic_stride4,
           'stride8': traffic_stride8,
           'stag0203': traffic_stag0203,
           'stag0503': traffic_stag0503,
           'random': traffic_random,
           'bijective': traffic_bijective,
           'hotspot': traffic_hotspot}


def main():
    args = parser.parse_args()
    if args.pattern not in TRAFFIC:
        raise Exception('Unrecognized traffic pattern "%s"' % args.pattern)
    traffic = TRAFFIC[args.pattern]()
    print json.dumps(traffic)

if __name__ == '__main__':
    main()
