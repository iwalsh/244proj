Stanford CS244 Final Project
============================

This is an implementation of the Hedera controller supporting Global First Fit from http://bnrg.cs.berkeley.edu/~randy/Courses/CS294.S13/7.3.pdf. 

It is built on top of Brandon Heller's Ripl library and POX controller with minor changes to both to support version consistency and Hedera functionality.

Use a CS 244 Mininet VM to run the code (either from the class website or an Amazon EC2 instance).

1. Switch to the CS 244 version of Mininet

    `$ cd ~/mininet`

    `$ git checkout -b cs244 origin/class/cs244`

2. Fix the module dependencies for this version

    `$ vim ~/mininet/mininet/moduledeps.py`

    (^change this line: "-OVS_KMOD = 'openvswitch_mod'"
                    to: "OVS_KMOD = 'openvswitch'")

3. Install the correct version

    `$ cd ~/mininet`

    `$ sudo make install`

4. Switch to the 'dart' branch of POX

    `$ cd ~/pox`

    `$ git checkout dart`

    `$ git pull origin dart`

5. Clone our project repo

    `$ cd ~`

    `$ git clone https://github.com/iwalsh/244proj.git`

    `cd 244proj/`

    `$ sudo python setup.py install`

6. Run it!

    `$ cd ~/244proj`

    `$ sudo ./run.sh`

7. Plot the results

    `$ cd ~/244proj`

    `$ python plot_results myAwesomePlot.png`

BONUS:

If you don't want to run the full measurement suite, you can run one measurement
at a time, like so:

`$ cd ~/244proj`

Terminal #1 - start the remote controller using ECMP flow scheduling

`$ ~/pox/pox.py controllers.riplpox --topo=ft,4 --routing=hashed --mode=reactive`

Terminal #2 - run our measurement script on a sample traffic pattern

`$ sudo python hedera.py ecmp traffic/stride2.json`

Alternate Terminal #1 - start the Hedera controller using Global First-Fit flow scheduling

`~/pox/pox.py controllers.hederaController --topo=ft,4`
