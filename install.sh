#!/bin/bash
# Adrian Vollmer, SySS GmbH 2019


function usage {
    cat << EOF
This script prepares a remote machine (should be Kali Linux) via SSH for the Lauschgerät.

Usage:
$0 [options ...] <SSHSERVER> <ATIF> <CLIF> <SWIF> [<WIFIIF> <WIFI-PASSWORD>]

Positional arguments:

    <SSHSERVER>:
        The host name of the remote machine

    <ATIF>:
        The name of the interface connected used to manage the Lauschgerät
        (attacker interface)

    <CLIF>:
        The name of the interface connected to the victim client

    <SWIF>:
        The name of the interface connected to the victim switch

    <WIFIIF>:
        The name of the wifi interface on the remote machine

        If the remote machine is virtual, try passing a USB wifi dongle to
        the machine.

    <WIFI-PASSWORD>:
        The password for the wifi network created by the Lauschgerät

        Must be at least eight characters long.

        WARNING: Knowing this password is equivalent to having root access!

The options are:

    -p=<PORT>, --port=<PORT>:
        The port of the SSH server (default: 22)

    -u=<USER>, --user=<USER>:
        The user to authenticate as (default: root)

    --dhcp:
        Set up a DHCP server on ATIF interface of the remote machine (default: no)

        This should not be necessary if the remote machine is virtual. If it
        is physical, you probably want this option.

    -h, --help:
        Print this message and quit
EOF
}

set -e

for i in "$@" ; do
    case $i in
            -s=*|--server=*)
            SERVER="${i#*=}"
            shift # past argument=value
        ;;
            -p=*|--port=*)
            PORT="${i#*=}"
            shift # past argument=value
        ;;
            -u=*|--user=*)
            SSHUSER="${i#*=}"
            shift # past argument=value
        ;;
            -h|--help)
            usage
            exit 0
        ;;
            --dhcp)
            DHCP=YES
            shift # past argument with no value
        ;;
            -*)
            echo "Unknown option: $i"
            exit 1
        ;;
        *)
            break      # unknown option
        ;;
    esac
done


SERVER="$1"
ATIF="$2"
CLIF="$3"
SWIF="$4"
WIFIIF="$5"
WIFIPASS="$6"

[ -z "$PORT" ] && PORT=22
[ -z "$SSHUSER" ] && SSHUSER=root
[ -z "$DHCP" ] && DHCP=NO

set -u

TARBALL=/tmp/lg.tar.gz
BOOTSTRAP_DIR="$(dirname "$0")/bootstrap"


if [ -z "$SERVER" -o -z "$ATIF" -o -z "$CLIF" -o -z "$SWIF" ]; then
    usage
    exit 1
fi

tar czf "$TARBALL" -C "$(dirname "$0")" \
    --exclude=.git \
    --exclude=doc \
    --exclude=testing \
    ./*

echo "WARNING: This will overwrite many system files on the target system!"
echo "Don't do this if you want to use the system for anything but a Lauschgerät."
echo "Do you want to proceed? [y/N] "
read decision
if [ ! $decision = y ] ; then
    echo "Aborting"
    exit 0
fi

NOW="$(date "+%F %T")"
ssh-copy-id -p "$PORT" "$SSHUSER@$SERVER" || true
scp -P "$PORT" "$TARBALL" "$SSHUSER@$SERVER:/root"
ssh -p "$PORT" "$SSHUSER@$SERVER" "date -s "$NOW"; mkdir -p /root/lg ; cd /root/lg ; \
    tar xf ../lg.tar.gz ; \
    /root/lg/lg-server/lg-setup.sh \
    \"$DHCP\" \"$ATIF\" \"$CLIF\" \"$SWIF\" $WIFIIF $WIFIPASS"
