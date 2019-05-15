#!/bin/bash
# Adrian Vollmer, SySS GmbH 2019

set -e

SERVER="$1"
PORT="$2"
[ -z "$PORT" ] && PORT=22

set -u

TARBALL=/tmp/lg.tar.gz
BOOTSTRAP_DIR="$(dirname "$0")/bootstrap"

ATIF=
CLIF=
SWIF=
WIFIIF=
WIFIPASS=

if [ -z "$SERVER" ]; then
    cat << EOF
This script prepares a remote machine (should be Kali Linux) via SSH for the Lauschgerät.

Usage:
$0 [<USER>@]<SSHSERVER> [<PORT>]
EOF
    exit 1
fi

tar \
    --exclude=".*" \
    --exclude=testing \
    czf "$TARBALL" -C "$(dirname "$0")" \
    "lg-server" \
    "lauschgeraet" \
    "lauschgerät.py"

echo "WARNING: This will overwrite many system files on the target system!"
echo "Don't do this if you want to use the system for anything but a Lauschgerät."
echo "Do you want to proceed? [y/N] "
read decision
if [ ! $decision = y ] ; then
    echo "Aborting"
    exit 0
fi

scp -P "$PORT" "$TARBALL" "$SERVER:/root"
ssh -p "$PORT" "$SERVER" "/root/lg/lg-server/lg-setup.sh \
    \"$ATIF\" \"$CLIF\" \"$SWIF\" $WIFIIF $WIFIPASS"
