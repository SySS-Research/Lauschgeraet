
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
