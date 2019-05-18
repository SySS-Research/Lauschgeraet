#!/bin/bash
#Adrian Vollmer, SySS GmbH 2018

set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

if [[ $# -lt 4 ]] ; then
    echo "Usage: lg-setup.sh YES|NO <attacker interface> <client interface> <switch interface> [<wifi interface> <wpa2 passphrase>]"
    echo "Example: lg-setup.sh YES eth0 eth1 eth2 wlan0 Lauschgerät"
    exit 1
else
    DHCP=$1
    ATIF=$2
    CLIF=$3
    SWIF=$4
    WIFIIF=$5
    wifipw=$6
    if [ -z $WIFIIF ] ; then WIFIIF=none ; fi
fi

if [[ `cat /etc/issue` != Kali* ]] ; then
    echo "[!] Warning! This setup script is meant for Kali Linux only!"
    echo "    Things might not work properly and you should do a manual install."
fi

rootdir=`dirname $0`

echo "[*] Installing dependencies..."

apt-get update
apt-get -y dist-upgrade
cat "$rootdir/../requirements-system.txt" | xargs apt-get -y install
pip3 install --user -r "$rootdir/../requirements.txt"


echo "[*] Copying config files..."

cp $rootdir/conf/lauschgeraet.service /lib/systemd/system/
cp $rootdir/conf/motd /etc/motd
cp $rootdir/conf/sysctl.conf /etc/sysctl.conf
cp $rootdir/conf/modules /etc/modules
cp $rootdir/conf/lauschgeraet.profile /etc/profile.d/

if [ $DHCP = YES -o $WIFIIF != none ] ; then
    cp $rootdir/conf/dnsmasq.conf /etc/dnsmasq.conf
fi

if [[ $DHCP = YES ]] ; then
    cp $rootdir/conf/sshd_config /etc/ssh/sshd_config
    cp $rootdir/conf/interfaces.atif /etc/network/interfaces.d/lauschgeraet.atif
    sed -i "s/^#ATDHCP#//" /etc/dnsmasq.conf
    sed -i "s/%ATIF%/$ATIF/g" /etc/dnsmasq.conf /etc/network/interfaces.d/lauschgeraet.atif
fi

sed -i "s/%ATIF%/$ATIF/g" $rootdir/bin/lg-config.sh
sed -i "s/%CLIF%/$CLIF/g" $rootdir/bin/lg-config.sh /lib/systemd/system/lauschgeraet.service
sed -i "s/%SWIF%/$SWIF/g" $rootdir/bin/lg-config.sh /lib/systemd/system/lauschgeraet.service

if [[ $WIFIIF != none ]] ; then
    cp $rootdir/conf/hostapd.conf /etc/hostapd/hostapd.conf
    chmod 600 /etc/hostapd/hostapd.conf
    cp $rootdir/conf/hostapd /etc/default/hostapd
    cp $rootdir/conf/interfaces.wifi /etc/network/interfaces.d/lauschgeraet.wifi
    sed -i "s/%WIFIIF%/$WIFIIF/g" /etc/hostapd/hostapd.conf /etc/dnsmasq.conf /etc/network/interfaces.d/lauschgeraet.wifi $rootdir/bin/lg-config.sh
    sed -i "s/^#WIFI#//" /etc/dnsmasq.conf $rootdir/bin/lg-config.sh
    sed -i "s/^wpa_passphrase=.*\$/wpa_passphrase=$wifipw/" /etc/hostapd/hostapd.conf
    update-rc.d hostapd defaults
fi

echo "[*] Configuring services..."

update-rc.d ssh defaults
if [ $DHCP = YES -o $WIFIIF != none ] ; then
    update-rc.d dnsmasq defaults
    update-rc.d networking defaults
fi
if [ $DHCP = YES -a $WIFIIF != none ] ; then
    update-rc.d dhcpcd remove
fi

sleep 1

systemctl enable lauschgeraet
apt-get remove avahi-daemon || true
systemctl disable systemd-timesyncd.service || true

echo "[*] Done! Reboot now."
