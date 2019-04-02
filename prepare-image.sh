#!/bin/bash
# Adrian Vollmer, SySS GmbH 2019
# This script takes a raspbian img and prepares it to be a Lauschgerät
# i.e. it installs a systemd service and copies the app as a tarball

set -e

IMG="$1"
PORT="$2"

set -u

TARBALL=/tmp/lg.tar.gz
BOOTSTRAP_DIR="$(dirname "$0")/bootstrap"

if [ -z "$IMG" ]; then
    cat << EOF
This script prepares a Raspbian image or a remote machine via SSH for the Lauschgerät.

Usage:
$0 <PATH>|<SSHSERVER> [<PORT>]
EOF
    exit 1
fi

tar czf "$TARBALL" -C "$(dirname "$0")" --exclude=testing \
    "lg-server" \
    "lauschgeraet" \
    "lauschgerät.py"

if [ -f "$IMG" ] ; then
    echo "Checking prerequisites..."

    for com in guestfish ; do
        command -v "$com" >/dev/null 2>&1 || {
            echo >&2 "$com required, but it's not installed. Aborting."
            exit 1
        }
    done

    echo "All good, preparing the image..."


    guestfish -a "$IMG" -m /dev/sda2 <<_EOF_
copy-in $BOOTSTRAP_DIR/lauschgeraetd /usr/sbin
copy-in $TARBALL /root/
copy-in $BOOTSTRAP_DIR/lauschgeraet.service /lib/systemd/system/
ln-s /lib/systemd/system/lauschgeraet.service /etc/systemd/system/multi-user.target.wants/lauschgeraet.service
_EOF_
else
    [ -z "$PORT" ] && PORT=22
    scp -P "$PORT" $TARBALL $BOOTSTRAP_DIR/lauschgeraet.service $BOOTSTRAP_DIR/lauschgeraetd "$IMG:/root/"
    ssh -p "$PORT" $IMG "ln -s /lib/systemd/system/lauschgeraet.service \
    /etc/systemd/system/multi-user.target.wants/lauschgeraet.service; \
    cp /root/lauschgeraetd /usr/sbin; \
    cp /root/lauschgeraet.service /lib/systemd/system/"
fi

rm -f "$TARBALL"

echo "Done. Put the image on an SD card and boot your device. Plug it into a
network where DHCP is provided and find its IP address. Then connect to the
webapp on port 1337 and follow the instructions."
