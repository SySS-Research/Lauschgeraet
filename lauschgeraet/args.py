import argparse

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
