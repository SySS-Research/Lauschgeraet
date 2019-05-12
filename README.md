
Installation
============

The recommended distribution is always Kali (even on ARM).

Variant 1 (namespaces)
----------------------

Install the requirements:

    cat requirements-system.txt | xargs sudo apt-get -y install
    pip3 install --user -r requirements.txt

Variant 2 (virtual machine)
---------------------------

Make sure the virtual machine is exposing an SSH service and root is allowed
to log in via SSH. Then run:

    install.sh root@<HOST> <PORT>

Variant 3 (hardware)
--------------------

Download a suitable [Kali Linux image for
ARM](https://www.offensive-security.com/kali-linux-arm-images/) and run:

    install.sh <PATH-TO-IMAGE>

Then copy the image on a Micro SD card:

    cp <PATH-TO-IMAGE> /dev/mmcblk0

(or whatever your device is named) and plug it into the Raspberry Pi or
Banana Pi. Put it into a network with a DHCP server, browse to
http://<IP>:1337 and follow the instructions.


Testing
=======

If you want to contribute, it's useful to have a good test setup. Since it's
a pain to work with another physical device, let's just the same machine
we're already working on. The trick is to use yet another network namespace.

The script `testsetup.sh` creates a network namespace with the name `ext` as
well as four virtual devices:

* `lg-eth0` - replaces the the interface on the attacker machine connect
  to the client
* `lg-eth1` - replaces the the interface on the attacker machine connect
  to the switch
* `lg-eth0-l` - replaces the interface of the victim client
* `lg-eth1-l` - replaces the interface of the victim switch

`lg-eth0-l` is assigned to the network namespace `ext` by the script. There
needs to be a DHCP service listening on `lg-eth1-l`. It can be in the
default network namespace.

To run a test, execute `./testsetup.sh ; ./lauschgerät.py -ci lg-eth0 -si
lg-eth1`. Now switch into the `ext` namespace with something like `sudo ip
netns exec ext bash`. Pretend to be the victim by placing requests from this
shell, preferably with `curl` or `wget`, but theoretically you can also
launch a browser.
