# plot_results.py
#
# Plot the results of total throughput for each traffic pattern and
# scheduling alogorithm.
#
# by Anh Truong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244, Spring 2015

import json
import matplotlib as m
import os
if os.uname()[0] == "Darwin":
    m.use("MacOSX")
else:
    m.use("Agg")

import matplotlib.pyplot as plt

from argparse import ArgumentParser

RESULTS_DIR = 'results/'

ECMP_MEAN = 'ecmp_mean_gbps'
ECMP_STDDEV = 'ecmp_stddev_gbps'
GFF_MEAN = 'gff_mean_gbps'
GFF_STDDEV = 'gff_stddev_gbps'

parser = ArgumentParser(description='Plotting Hedera results')
parser.add_argument('outfile', type=str, help='Where to save the plot')
args = parser.parse_args()


def load_data():
    """
    Outermost keys are the traffic patterns: 'stride1', 'stag0_0203', etc.
    They are mapped to the results dictionary from results/<traffic>.json.
    """
    data = {}

    for filename in os.listdir(RESULTS_DIR):
        datafile = RESULTS_DIR + filename
        label = filename.replace('.json', '')
        if os.path.isfile(datafile):
            with open(datafile, 'r') as f:
                data[label] = json.load(f)

    return data


def extract_means(data):
    """
    Return two lists of means, ordered by traffic pattern in data's keyset
    """
    means_ecmp = []
    means_gff = []

    for label in data:
        if ECMP_MEAN in data[label]:
            means_ecmp.append(data[label][ECMP_MEAN])
        else:
            means_ecmp.append(0.0)

        if GFF_MEAN in data[label]:
            means_gff.append(data[label][GFF_MEAN])
        else:
            means_gff.append(0.0)

    return (means_ecmp, means_gff)


def extract_stddevs(data):
    """
    Extract two lists of stddevs, ordered by traffic pattern
    """
    stddevs_ecmp = []
    stddevs_gff = []

    for label in data:
        if ECMP_STDDEV in data[label]:
            stddevs_ecmp.append(data[label][ECMP_STDDEV])
        else:
            stddevs_ecmp.append(0.0)

        if GFF_STDDEV in data[label]:
            stddevs_gff.append(data[label][GFF_STDDEV])
        else:
            stddevs_gff.append(0.0)

    return (stddevs_ecmp, stddevs_gff)


def plot(data):
    n_groups = len(data.keys())  # 1 group per traffic pattern

    (means_ecmp, means_gff) = extract_means(data)
    (stddevs_ecmp, stddevs_gff) = extract_stddevs(data)
    traffics = data.keys()

    fig, ax = plt.subplots()

    index = range(n_groups)
    bar_width = 0.35

    opacity = 0.4
    error_config = {'ecolor': '0.3'}

    rects1 = plt.bar(index, means_ecmp, bar_width,
                     alpha=opacity,
                     color='b',
                     yerr=stddevs_ecmp,
                     error_kw=error_config,
                     label='ECMP')

    index2 = map(lambda x: x + bar_width, index)
    rects2 = plt.bar(index2, means_gff, bar_width,
                     alpha=opacity,
                     color='r',
                     yerr=stddevs_gff,
                     error_kw=error_config,
                     label='Global first-fit')

    plt.xlabel('Traffic pattern')
    plt.ylabel('Total throughput')
    plt.title('Comparison of scheduling performance')
    plt.xticks(index2, traffics)
    plt.legend()

    plt.tight_layout()
    # plt.show()

    if os.path.exists(args.outfile):
        os.remove(args.outfile)

    plt.savefig(args.outfile)


def main():
    data = load_data()
    plot(data)
    print 'Plot saved to %s!' % args.outfile

if __name__ == '__main__':
    main()
