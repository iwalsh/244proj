# 244proj
Stanford CS244 Final Project
This is an implementation of the Hedera controller supporting Global First Fit from http://bnrg.cs.berkeley.edu/~randy/Courses/CS294.S13/7.3.pdf. 

It is built on top of Brandon Heller's Ripl library and POX controller with minor changes to both to support version consistency and Hedera functionality.

To run:
cd ~/mininet
git checkout -b cs244 origin/class/cs244
using whatever editor you prefer, open the file  mininet/moduledeps.py
change the line, "-OVS_KMOD = 'openvswitch_mod'" to "OVS_KMOD = 'openvswitch'"
cd ../
sudo make install

cd ~/pox
git checkout dart
git pull origin dart

Cloning this repository,
cd ~/244proj
sudo python setup.py install
