# measure_all_the_things.py
#
# Run the Mininet simulation and measure the resulting aggregate throughput
# for every (traffic, scheduling). This operation takes a long time: there
# are 17 traffic pattersn and 2 scheduling algorithms, and each run takes
# ~1 minute, so the full process takes 30-45 minutes!
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
    cmd = '~/pox/pox.py riplpox.riplpox --topo=ft,4 --routing=random --mode=reactive'
    subprocess.call(cmd, stdout=stdout_fd, stderr=subprocess.STDOUT, shell=True)


def run_gff_controller(stdout_fd):
    """
    Run the Hedera controller using Global First-Fit flow scheduling. Runs
    forever, so the parent should kill it when hedera.py is done.
    """
    cmd = '~/pox/pox.py controllers.hederaController --topo=ft,4'
    subprocess.call(cmd, stdout=stdout_fd, stderr=subprocess.STDOUT, shell=True)


def run_measurements(label, traffic_file, stdout_fd):
    """
    Run the hedera.py script to start Mininet and take one measurement of
    aggregate throughput for a single traffic pattern and controller. This
    completes in ~1 minute, so the caller blocks until it's done.
    """
    cmd = 'sudo python hedera.py %s %s' % (label, traffic_file)
    subprocess.call(cmd, stdout=stdout_fd, shell=True)


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

            controller = Process(target=run_ecmp_controller, args=(devnull,))
            controller.start()
            sleep(5)

            mininet = Process(target=run_measurements,
                              args=('ecmp', filepath, devnull))
            mininet.start()
            mininet.join()

            controller.terminate()
            print '\nFinished ECMP measurement in %02fs!' % (time() - start)
            sleep(5)

            # GFF measurement
            print '\nTaking the GFF measurement for %s...' % filepath
            print '====================================\n'
            start = time()

            controller = Process(target=run_gff_controller, args=(devnull,))
            controller.start()
            sleep(5)

            mininet = Process(target=run_measurements,
                              args=('gff', filepath, None))
            mininet.start()
            mininet.join()

            controller.terminate()
            print '\nFinished ECMP measurement in %02fs!' % (time() - start)
            sleep(5)

    print '\nAll done! Whew!'

if __name__ == '__main__':
    main()
