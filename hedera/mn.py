# mn.py
#
# Exports the Hedera fat-tree topology to Mininet.
#
# Based on the file of the same name in Brandon Heller's RiplPox project,
# available under the GPLv2 open-source license and hosted at
#     https://github.com/brandonheller/riplpox
#
# Example usage:
#     sudo mn --custom ~/244proj/hedera/mn.py --topo ft,4
#
# by Anh Truong and Ian Walsh
# for Stanford CS 244, Spring 2015

import sys
# FIXME: get the import to work without this hack!
sys.path.append("/home/mininet/244proj/")
import hedera.fattree

topos = {'ft': hedera.fattree.FatTreeTopo}
