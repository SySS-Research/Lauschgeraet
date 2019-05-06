if [ -z "$LG_ENV_BY_PYTHON" ] ; then
    ATIF='eth0' # Attacker
    CLIF='eth1' # Client
    SWIF='eth2' # Switch
    WIFIIF='wlan0' # Wifi
    # It should never be necessary to change the following values
    if [ ! -z "$PY_ATIF" ] ; then
        ATIF=$PY_ATIF
        CLIF=$PY_CLIF
        SWIF=$PY_SWIF
        WIFIIF=$PY_WIFIIF
    fi
    BRIF='br0'
    BRIP='192.0.2.1'
    GWIP='192.0.2.254' # bogus gateway
    ATNET='203.0.113.0/24'
    ATIP='203.0.113.1'
    WIFINET='198.51.100.0/24'
    RANGE=61000-62000
    TMPDIR="$BD/../.tmp/"
fi
mkdir -p $TMPDIR
STATUSFILE=$TMPDIR/status
