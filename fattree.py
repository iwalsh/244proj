# fattree.py

from mininet.topo import Topo


class FatTree(Topo):
    "Fat Tree Topology"

    # Example names for k=4
    def __init__(self, k, link_bw, delay):
        Topo.__init__(self)
        self.core_switches = {}
        self.agg_switches = {}
        self.edge_switches = {}
#        self.build(k, link_bw, delay)

#    def build(self, k, link_bw, delay):
        # Set up the (k/2)^2 core switches, c0 : c3
        core_switches = {}
        for i in xrange((k / 2) ** 2):
            name = 'c' + str(i)
            self.core_switches[name] = self.addSwitch(name)

        # Set up the k pods, each of k switches
        for pod in xrange(k):

            # First k/2 are aggregation switches, a0 : a1
            for agg in xrange(k / 2):
                name = 'a' + str(pod * (k / 2) + agg)
                agg_switch = self.addSwitch(name)
                self.agg_switches[name] = agg_switch

                # Each aggregation switch connects to k/2 core switches
                for c in xrange(k / 2):
                    core_switch = self.core_switches['c' + str(agg * (k / 2) + c)]
                    self.addLink(agg_switch, core_switch, bw=link_bw, delay=delay)

            # Second k/2 are edge switches, e0 : e1
            for edge in xrange(k / 2):
                name = 'e' + str(pod * (k / 2) + edge)
                edge_switch = self.addSwitch(name)
                self.edge_switches[name] = edge_switch

                # Each edge switch connects to k/2 agg switches (all in pod)
                for agg in xrange(k / 2):
                    agg_switch = self.agg_switches['a' + str(pod * (k / 2) + agg)]
                    self.addLink(edge_switch, agg_switch, bw=link_bw, delay=delay)

                # Each edge switch connects to k/2 end hosts
                for h in xrange(k / 2):
                    hostname = 'h' + str(pod * k + edge * (k / 2) + h)
                    host = self.addHost(hostname)
                    self.addLink(edge_switch, host, bw=link_bw, delay=delay)
