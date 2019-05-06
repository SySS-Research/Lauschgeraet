#!/bin/bash
# test script for lauschgerät
# run a DHCP server on $if2-l

if1="lg-eth2"
if2="lg-eth3"

ip netns del ext
ip link add $if1-l type veth peer name $if1
ip link add $if2-l type veth peer name $if2
ip netns add ext
ip link set $if1-l netns ext
ip link set $if2-l up
ip a a 192.168.7.1 $if2-l
ip netns exec ext ip l set $if1-l up
