# 244proj
Final project for CS 244


$ touch ~/244proj/'__init__.py'

$ touch ~/244proj/hedera/'__init__.py'

export PYTHONPATH=$HOME/244proj:$PYTHONPATH

Example invocation:

# Run HederaController in reactive mode w/random routing
cd ~/
~/pox/pox.py hedera.controller --topo=ft,4 --routing=random --mode=reactive

<<<<<<< Updated upstream
# Running Mininet w/a Fat Tree topology, in a second window:
cd ~/
sudo mn --custom ~/244proj/hedera/mn.py --topo ft,4 --controller=remote --mac
=======
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

    `$ sudo python measure_all_the_things.py results/`

7. Plot the results

    `$ cd ~/244proj`

    `$ python plot_results results/ myAwesomePlot.png`

BONUS:

If you don't want to run the full measurement suite, you can run one measurement
at a time, like so:

`$ cd ~/244proj`

Terminal #1 - start the remote controller using ECMP flow scheduling

`$ ~/pox/pox.py riplpox.riplpox --topo=ft,4 --routing=random --mode=reactive`

Terminal #2 - run our measurement script on a sample traffic pattern

`$ sudo python hedera.py ecmp traffic/stride2.json results`

Alternate Terminal #1 - start the Hedera controller using Global First-Fit flow scheduling

`~/pox/pox.py controllers.hederaController --topo=ft,4`
>>>>>>> Stashed changes
