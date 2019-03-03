#!/bin/bash
# Adrian Vollmer, SySS GmbH 2019
# This script takes a raspbian img and prepares it to be a Lauschgerät
# i.e. it installs a systemd service and copies the app as a tarball

set -e
set -u

IMG=

echo "Checking prerequisites..."

for com in guestfish ; do
    command -v "$com" >/dev/null 2>&1 || {
        echo >&2 "$com required, but it's not installed. Aborting."
        exit 1
    }
done

echo "All good, preparing the image..."

#TODO create tar.gz

guestfish -a "$IMG" -m /dev/sda2 <<_EOF_
copy-in lauschgeraetd /usr/bin
copy-in /tmp/lg.tar.gz /root/
copy-in lauschgeraet.service /lib/systemd/system/
ln-s /etc/systemd/system/lauschgeraet.service /etc/systemd/system/multi-user.target.wants/lauschgeraet.service
_EOF_

rm /tmp/lg.tar.gz

echo "Done. Put the image on an SD card and boot your device. Then connect
to the webapp on port 1337 and follow the instructions."
