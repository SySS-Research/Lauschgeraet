#!/bin/bash
#Adrian Vollmer, SySS GmbH 2018

set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

if [[ $# -lt 3 ]] ; then
    echo "Usage: lg-setup.sh <attacker interface> <client interface> <switch interface> [<wifi interface> <wpa2 passphrase>]"
    echo "Example: lg-setup.sh eth0 eth1 eth2 wlan0 Lauschgerät"
    exit 1
else
    ATIF=$1
    CLIF=$2
    SWIF=$3
    WIFIIF=$4
    wifipw=$5
    if [ -z $WIFIIF ] ; then WIFIIF=none ; fi
fi

if [[ `cat /etc/issue` != Raspbian* ]] ; then
    echo "[!] Warning! This setup script is meant for Raspbian only! Things
    might not work properly and you should do a manual install."
fi

rootdir=`dirname $0`

echo "[*] Installing dependencies..."

apt-get update
apt-get -y dist-upgrade
apt-get -y install dnsmasq hostapd tcpdump ebtables bridge-utils arptables \
    arp-scan inetutils-tools net-tools iproute2 python-scapy \
    python-netaddr python3 python3-flask python3-pip

pip3 install python-socketio

echo "[*] Copying config files..."

cp $rootdir/conf/motd /etc/motd
cp $rootdir/conf/dnsmasq.conf /etc/dnsmasq.conf
cp $rootdir/conf/interfaces.atif /etc/network/interfaces.d/lauschgeraet.atif
cp $rootdir/conf/hostapd.conf /etc/hostapd/hostapd.conf
chmod 600 /etc/hostapd/hostapd.conf
cp $rootdir/conf/hostapd /etc/default/hostapd
cp $rootdir/conf/sshd_config /etc/ssh/sshd_config
cp $rootdir/conf/sysctl.conf /etc/sysctl.conf
cp $rootdir/conf/modules /etc/modules
for file in $rootdir/bin/* ; do
    ln -s "$file" /usr/sbin
done

sed -i "s/%ATIF%/$ATIF/g" /etc/dnsmasq.conf /etc/network/interfaces.d/lauschgeraet.atif $rootdir/bin/lg-config.sh
sed -i "s/%CLIF%/$CLIF/g" $rootdir/bin/lg-config.sh
sed -i "s/%SWIF%/$SWIF/g" $rootdir/bin/lg-config.sh


if [[ $WIFIIF != none ]] ; then
    cp $rootdir/conf/interfaces.wifi /etc/network/interfaces.d/lauschgeraet.wifi
    sed -i "s/%WIFIIF%/$WIFIIF/g" /etc/hostapd/hostapd.conf /etc/dnsmasq.conf /etc/network/interfaces.d/lauschgeraet.wifi $rootdir/bin/lg-config.sh
    sed -i "s/^#WIFI#//" /etc/dnsmasq.conf $rootdir/bin/lg-config.sh
    sed -i "s/^wpa_passphrase=.*\$/wpa_passphrase=$wifipw/" /etc/hostapd/hostapd.conf
    update-rc.d hostapd defaults
fi

echo "[*] Configuring services..."

update-rc.d ssh defaults
update-rc.d dnsmasq defaults
update-rc.d networking defaults
update-rc.d dhcpcd remove
sleep 1
apt-get remove avahi-daemon || true
systemctl disable systemd-timesyncd.service || true

echo "[*] Done!"
echo "[*] You may want to choose a new password for user 'pi' with 'passwd pi' and then reboot."
