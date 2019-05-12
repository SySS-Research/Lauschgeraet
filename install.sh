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
$0 <SSHSERVER> [<PORT>]
EOF
    exit 1
fi

tar czf "$TARBALL" -C "$(dirname "$0")" --exclude=testing \
    "lg-server" \
    "lauschgeraet" \
    "lauschgerät.py"

[ -z "$PORT" ] && PORT=22
scp -P "$PORT" $TARBALL $BOOTSTRAP_DIR/lauschgeraet.service $BOOTSTRAP_DIR/lauschgeraetd "$IMG:/root/"
ssh -p "$PORT" $IMG "ln -s /lib/systemd/system/lauschgeraet.service \
/etc/systemd/system/multi-user.target.wants/lauschgeraet.service; \
cp /root/lauschgeraetd /usr/sbin; \
cp /root/lauschgeraet.service /lib/systemd/system/"

rm -f "$TARBALL"

echo "Done"
