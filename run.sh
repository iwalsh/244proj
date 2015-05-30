#!/bin/bash
for file in traffic/*
do
	killall -9 python2.7
	~/pox/pox.py controllers.riplpox --topo=ft,4 --routing=hashed --mode=reactive &
	sleep 2
	sudo python hedera.py ecmp $file
	sleep 6
done

for file in traffic/*
do
 	killall -9 python2.7
	~/pox/pox.py controllers.hederaController --topo=ft,4 &
	sleep 2
	sudo python hedera.py gff $file
	sleep 6
done