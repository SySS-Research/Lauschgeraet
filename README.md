Lauschgerät
===========

Analyze and modify traffic without worrying about TLS or 802.1X.

Lauschgerät attempts to do most of the heavy lifting so you can focus on
things that cannot be done by a machine. Get an extra ethernet cable, plug
your machine between two test machines, and watch and control the traffic
flowing through your machine.

Installation
============

The recommended distribution is always Kali Linux (even on ARM). A minimal
network install with just an SSH server and standard Linux tools will do.

Variant 1 (namespaces)
----------------------

Install the requirements:

    cat requirements-system.txt | xargs sudo apt-get -y install
    pip3 install --user -r requirements.txt

Variant 2 (virtual machine)
---------------------------

Make sure the virtual machine is exposing an SSH service, has access to the
internet and root is allowed to log in via SSH. Then run:

    install.sh root@<HOST> <PORT>

Variant 3 (hardware)
--------------------

Download a suitable [Kali Linux image for
ARM](https://www.offensive-security.com/kali-linux-arm-images/), install it
on a Raspberry Pi, Banana Pi or some other compatible device, make sure you
got root access via SSH and that the device has internet access, and proceed
as in variant 2.

This is a good moment to get coffee, because this step may take a while.

Usage
=====

Quickstart
----------

1. Attach the victim client and the victim switch to the Lauschgerät
2. If using variant 1 (network namespaces), run `lauschgeraet.py
   <client-interface> <switch-interface>`
3. Navigate a browser to the attacker machine on port 1337
4. Set the status of the Lauschgerät to `passive`
5. Watch the traffic with `ip netns exec lg tcpdump -i br0`, or remotely
   with Wireshark: `ssh root@kali ip netns exec lg tcpdump -s 0 -U -n -w - -i br0 | wireshark -k -i -`
6. To redirect traffic to another service, set the status of the Lauschgerät
   to `active`
7. Run a service on the target port using the "Services" page
7. Define an `iptables` rule on the "Man in the Middle" page that redirects
   traffic to that target port

Examples
--------

### TLS Eraser

### Flipper

Run the Flipper service (analogous to TLS Eraser) to flip images:

![Flipper](https://github.com/SySS-Research/Lauschgeraet/blob/master/doc/img/blackhat-flipped.png)

Shout out to byt3bl33d3r!

Testing
=======

If you want to contribute, it's useful to have a good test setup. Since it's
a pain to work with another physical device, let alone two more devices,
let's just use the same machine we're already working on (variant 1). The
trick is to use yet another network namespace.

The script `testsetup.sh` creates a network namespace with the name `ext` as
well as four virtual devices:

* `lg-eth0` - replaces the the interface on the attacker machine connected
  to the client
* `lg-eth1` - replaces the the interface on the attacker machine connected
  to the switch
* `lg-eth0-l` - replaces the interface of the victim client
* `lg-eth1-l` - replaces the interface of the victim switch

`lg-eth0-l` is assigned to the network namespace `ext` by the script. There
needs to be a DHCP service listening on `lg-eth1-l`. It can be in the
default network namespace.

To run a test, execute `./testsetup.sh ; ./lauschgeraet.py -ci lg-eth0 -si
lg-eth1`. Now switch into the `ext` namespace with something like `sudo ip
netns exec ext bash`. Pretend to be the victim by placing requests from this
shell, preferably with `curl` or `wget`, but you can also launch a browser.

Close all shells living in this new network namespace before you delete it.

Author
======

Adrian Vollmer, SySS GmbH 2018-2019

Disclaimer
==========

Use at your own risk. Do not use without full consent of everyone involved.
For educational purposes only.
