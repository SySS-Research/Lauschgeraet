#!/bin/bash
# Adrian Vollmer, SySS GmbH 2019
# This script takes a raspbian img and prepares it to be a Lauschgerät
# i.e. it installs a systemd service and copies the app as a tarball

set -e
set -u

IMG=
TARBALL=/tmp/lg.tar.gz

echo "Checking prerequisites..."

for com in guestfish ; do
    command -v "$com" >/dev/null 2>&1 || {
        echo >&2 "$com required, but it's not installed. Aborting."
        exit 1
    }
done

echo "All good, preparing the image..."

tar cf "$TARBALL" -C "$(dirname "$0")" lg-server

guestfish -a "$IMG" -m /dev/sda2 <<_EOF_
copy-in $(dirname $0)/lauschgeraetd /usr/bin
copy-in $TARBALL /root/
copy-in $(dirname $0)/lauschgeraet.service /lib/systemd/system/
ln-s /lib/systemd/system/lauschgeraet.service /etc/systemd/system/multi-user.target.wants/lauschgeraet.service
_EOF_

rm -f "$TARBALL"

echo "Done. Put the image on an SD card and boot your device. Then connect
to the webapp on port 1337 and follow the instructions."
