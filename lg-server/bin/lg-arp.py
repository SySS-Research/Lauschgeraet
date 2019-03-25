#!/usr/bin/env python2
#
# https://blog.to.com/netzwerkzugangskontrolle-nach-802-1x-2004-umgehen/
# Requires IF set to promiscous for MAC != interface MAC
# https://github.com/secdev/scapy/issues/17
import sys
import argparse
import logging
import netaddr
import re
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

###############################################################################
def getargs(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", metavar="MAC", nargs=1, dest="mac",
        help="source mac address, default is interface MAC")
    parser.add_argument("-a", metavar="ADDRESS", dest="adr", nargs=1,
        help="source IP, default is interface IP")
    parser.add_argument("-i", metavar="INTERFACE", dest="iface", nargs=1,
        required=True, help="source interface")
    parser.add_argument("network", type=str,
        help="network to scan in CIDR notation")
    return parser.parse_args(argv)

def main(argv):
    args = getargs(argv)
    mac = None
    adr = None

    if(args.mac):
        if(not re.match('^((([a-f]|[A-F]|[0-9]){2}):){5}([a-f]|[A-F]|[0-9]){2}$',
            args.mac[0])):
            print("Not a valid MAC address.")
            return(1)
        mac = args.mac[0]

    if(args.adr):
        try:
            ip = netaddr.IPAddress(args.adr[0])
        except netaddr.AddrFormatError as err:
            print("IP address {0}".format(err))
            return(1)
        except:
            print("Unexpected error: {0}".format(sys.exc_info()[0]))
            raise
        if(ip.version != 4):
            print("Source not an IPv4 address or network.")
            return(1)
        adr = str(ip)

    try:
        net = netaddr.IPNetwork(args.network);
    except netaddr.AddrFormatError as err:
        print("Network address {0}".format(err))
        return(1)
    except:
        print("Unexpected error: {0}".format(sys.exc_info()[0]))
        raise

    if(net.version != 4):
        print("Target is not an IPv4 address or network.")
        return(1)

    qpkt = []
    for ip in net.iter_hosts():
        p = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=str(ip))
        if(mac):
            p.src = mac
            p[ARP].hwsrc = mac
        if(adr):
            p[ARP].psrc = adr
        qpkt.append(p)

    try:
        (ans, unans) = srp(qpkt, iface=args.iface[0], verbose=0, timeout=1)
    except socket.error as err:
        print("Socket error: {0}".format(err))
        return(1)
    except:
        print("Unexpected error: {0}".format(sys.exc_info()[0]))
        raise

    ans.summary(lambda(s, r): r.sprintf("%ARP.hwsrc% %ARP.psrc%"))
    return(0)

###############################################################################
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
