import argparse
import logging

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description="Eavesdrop easily on wired connections"
)

parser.add_argument(
    '-ci',
    '--client-interface',
    default=None,
    dest="CL_IFACE",
    type=str,
    help="the name of the client interface"
)

parser.add_argument(
    '-si',
    '--switch-interface',
    default=None,
    dest="SW_IFACE",
    type=str,
    help="the name of the switch interface"
)

args = parser.parse_args()

if ((args.SW_IFACE is None) ^ (args.CL_IFACE is None)):
    log.critical("Only one of CL_IFACE or SW_IFACE has been specified. "
                 "Either define both or none.")

# we need to differentiate between the cases where we use network namespaces
# on a regular system or have our own dedicated system, like raspberry pi
LG_NS_MODE = args.SW_IFACE and args.CL_IFACE
