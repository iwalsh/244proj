# measure_all_the_things.py
#
# Run the Mininet simulation and measure the resulting aggregate throughput
# for every (traffic, scheduling).
#
# This operation can take a long time: there are 17 traffic patters and 2
# scheduling algorithms, and each of the 34 runs takes from ~30 seconds
# (on a fast EC2 instance) to ~2 minutes (on a slow laptop VM).
#
# Usage:
#     $ cd ~/244proj/
#     $ sudo python measure_all_the_things.py
#
# by Anh Trong (anhlt92)
# and Ian Walsh (iwalsh)
# for CS 244, Spring 2015

import os
import subprocess
from multiprocessing import Process
from time import sleep, time

TRAFFIC_DIR = 'traffic/'
RESULTS_DIR = 'all_the_things/'


def run_ecmp_controller(stdout_fd):
    """
    Run the POX controller using ECMP flow scheduling. This runs forever, so
    it must be killed by the parent process.
    """
    cmd = '/bin/sh -c ~/pox/pox.py controllers.riplpox --topo=ft,4 --routing=hashed --mode=reactive'
    return subprocess.Popen(cmd.split())


def run_gff_controller(stdout_fd):
    """
    Run the Hedera controller using Global First-Fit flow scheduling. Runs
    forever, so the parent should kill it when hedera.py is done.
    """
    cmd = '/bin/sh -c ~/pox/pox.py controllers.hederaController --topo=ft,4'
    return subprocess.Popen(cmd.split())


def run_measurements(label, traffic_file):
    """
    Run the hedera.py script to start Mininet and take one measurement of
    aggregate throughput for a single traffic pattern and controller. This
    completes in ~1 minute, so the caller blocks until it's done.
    """
    cmd = 'sudo python hedera.py %s %s' % (label, traffic_file)
    return subprocess.Popen(cmd.split())


def main():
    if not os.path.isdir(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)

    for name in os.listdir(TRAFFIC_DIR):
        filepath = TRAFFIC_DIR + name
        if not (os.path.isfile(filepath) and filepath.endswith('.json')):
            continue

        with open('/dev/null', 'w') as devnull:
            # ECMP measurement
            print '\nTaking the ECMP measurement for %s...' % filepath
            print '=====================================\n'
            start = time()

            controller = run_ecmp_controller(devnull)
            sleep(2)

            mininet = run_measurements('ecmp', filepath)
            mininet.wait()

            controller.kill()
            print '\nFinished ECMP measurement in %02fs!' % (time() - start)
            sleep(5)

            # GFF measurement
            print '\nTaking the GFF measurement for %s...' % filepath
            print '====================================\n'
            start = time()

            controller = run_gff_controller(devnull)
            sleep(2)

            mininet = run_measurements('gff', filepath)
            mininet.wait()

            controller.kill()
            print '\nFinished ECMP measurement in %02fs!' % (time() - start)
            sleep(5)

    print '\nAll done! Whew!'

if __name__ == '__main__':
    main()
