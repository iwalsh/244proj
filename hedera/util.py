# util.py
#
# Utility functions for Hedera toplogy & controller.
#
# Based on the file of the same name from Brandon Heller's RiplPOX project,
# available under the GPLv2 open-source license and hosted at
#     https://github.com/brandonheller/riplpox
#
# by Anh Truong and Ian Walsh
# for Stanford CS 244, Spring 2015


from mininet.util import makeNumeric

from hedera.routing import STStructuredRouting, RandomStructuredRouting
from hedera.routing import HashedStructuredRouting


def build_topo(topo, topos):
    "Create topology from string with format (object, arg1, arg2,...)."
    topo_split = topo.split(',')
    topo_name = topo_split[0]
    topo_params = topo_split[1:]

    # Convert int and float args; removes the need for every topology to
    # be flexible with input arg formats.
    topo_seq_params = [s for s in topo_params if '=' not in s]
    topo_seq_params = [makeNumeric(s) for s in topo_seq_params]
    topo_kw_params = {}
    for s in [p for p in topo_params if '=' in p]:
        key, val = s.split('=')
        topo_kw_params[key] = makeNumeric(val)

    if topo_name not in topos.keys():
        raise Exception('Invalid topo_name %s' % topo_name)
    return topos[topo_name](*topo_seq_params, **topo_kw_params)


DEF_ROUTING = 'st'
ROUTING = {
    'st': STStructuredRouting,
    'random': RandomStructuredRouting,
    'hashed': HashedStructuredRouting
}


def get_routing(routing_type, topo):
    "Return Ripl Routing object given a type and a Topo object"
    if routing_type is None:
        routing_type = DEF_ROUTING
    if routing_type not in ROUTING:
        raise Exception("unknown routing type %s not in %s" % (routing_type,
                                                               ROUTING.keys()))
    return ROUTING[routing_type](topo)
