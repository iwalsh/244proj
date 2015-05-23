# 244proj
Final project for CS 244


$ touch ~/244proj/'__init__.py'

$ touch ~/244proj/hedera/'__init__.py'

export PYTHONPATH=$HOME/244proj:$PYTHONPATH

Example invocation:

# Run HederaController in reactive mode w/random routing
cd ~/
~/pox/pox.py hedera.controller --topo=ft,4 --routing=random --mode=reactive

# Running Mininet w/a Fat Tree topology, in a second window:
cd ~/
sudo mn --custom ~/244proj/hedera/mn.py --topo ft,4 --controller=remote --mac
