ATIF='eth0' # Attacker
CLIF='eth1' # Client
SWIF='eth2' # Switch
WIFIIF='wlan0' # Wifi
# It should never be necessary to change the following values
BRIF='br0'
BRIP='192.0.2.1'
GWIP='192.0.2.254' # bogus gateway
ATNET='203.0.113.0/24'
WIFINET='198.51.100.0/24'
RANGE=61000-62000
TMPDIR=/tmp/lauschgereat
mkdir -p $TMPDIR
