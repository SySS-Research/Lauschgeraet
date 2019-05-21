# -*- coding: utf-8 -*-

from lauschgeraet.args import args, LG_NS_MODE
import subprocess
import os
import sys
import logging
import netns
log = logging.getLogger(__name__)


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


TEST = os.path.exists('testing')
TEST_STATE = {
            "lgstate": {
                "enabled": True,
                "active": True,
                "wifi": False,
                "status": "active",
            }
        }
LG_NS = "lg"

# set environment variables for the bash scripts
py_env = {
    "LG_ENV_BY_PYTHON": "1",
    "ATIF": "lgPeer",
    "SWIF": args.SW_IFACE,
    "CLIF": args.CL_IFACE,
    "GWIF": "lgGateway",
    "WIFIIF": "",
    "BRIF": 'br0',
    "BRIP": '192.0.2.1',
    "GWIP": '192.0.2.254',  # bogus gateway
    "ATNET": '203.0.113.0/24',
    "ATIP": '203.0.113.1',
    "WIFINET": '198.51.100.0/24',
    "RANGE": "61000-62000",
    "TMPDIR": os.path.join(
        get_script_path(),
        "lg-server",
        ".tmp",
    )
}

ns_setup = [
    # clean up status file: always start disabled
    'rm -f %s/status' % py_env["TMPDIR"],

    # create a network namespace
    'ip netns add ' + LG_NS,

    # Assign the interfaces to the new network namespace
    'ip link set netns %s %s' % (LG_NS, py_env["SWIF"]),
    'ip link set netns %s %s' % (LG_NS, py_env["CLIF"]),

    # create a pair of veth interfaces
    'ip link add %s type veth peer name %s' % (py_env["GWIF"], py_env["ATIF"]),

    # Assign the AT interface to the network namespace
    'ip link set netns %s %s' % (LG_NS, py_env["ATIF"]),

    # Assign an address to the gateway interface
    'ip addr add %s dev %s' % (py_env["ATNET"].replace('.0/', '.2/'),
                               py_env["GWIF"]),
    'ip link set %s up' % py_env["GWIF"],
    # Assign an address to the attacker interface
    'ip netns exec %s ip addr add %s/24 dev %s' % (
        LG_NS,
        py_env["ATIP"],
        py_env["ATIF"]),
    'ip netns exec %s ip link set %s up' % (LG_NS, py_env["ATIF"]),

    # Set loopback up
    'ip netns exec %s ip link set lo up',

    # Arrange to masquerade outbound packets from the network
    # namespace.
    'iptables -t nat -A POSTROUTING -o %s -j MASQUERADE' % py_env["GWIF"],
]

ns_teardown = [
    'ip netns del %s' % LG_NS,
    'ip link del %s' % py_env["GWIF"],
    'iptables -t nat -D POSTROUTING -o %s -j MASQUERADE' % py_env["GWIF"],
]


def run_steps(steps, ignore_errors=False):
    for step in steps:
        try:
            subprocess.check_output(step.split(),)
        except subprocess.CalledProcessError:
            if ignore_errors:
                log.exception("Exception while managing network namespaces:")
                break
            else:
                raise


def init_ns():
    if LG_NS_MODE:
        log.info("Creating network namespace")
        run_steps(ns_setup)


def teardown_ns():
    if LG_NS_MODE:
        log.info("Removing network namespace")
        run_steps(ns_teardown, True)


def lg_exec(*args):
    cmd = [
        os.path.join(
            get_script_path(),
            "lg-server",
            "bin",
            args[0],
        )
    ] + list(args[1:])
    my_env = {**os.environ.copy(), **py_env}
    try:
        if LG_NS_MODE:
            with netns.NetNS(nsname=LG_NS):
                output = subprocess.check_output(cmd,
                                                 env=my_env,
                                                 stderr=subprocess.STDOUT)
        else:
            output = subprocess.check_output(cmd,
                                             env=my_env,
                                             stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        log.exception("Exception while running command: %s" % ' '.join(args))
        log.error(e.output.decode())
        return b""
    return output


def get_lg_status():
    if TEST:
        return TEST_STATE
    output = lg_exec('lg', 'status')
    output = output.replace(b'\n', b'').decode()
    # the cmd returns one of the following:
    # * passive
    # * active
    # * wifi
    # * disabled
    # * waiting
    # * failed
    return {
        "lgstate": {
            "enabled": not output == 'disabled',
            "active": output == 'active',
            "wifi": output == 'wifi',
            "status": output,
        }
    }


def set_lg_status(mode):
    log.info("Setting Lauschgerät to '%s'" % mode)
    if TEST:
        global TEST_STATE
        output = mode
        TEST_STATE = {
            "lgstate": {
                "enabled": not output == 'disabled',
                "active": output == 'active',
                "wifi": output == 'wifi',
                "status": output,
            }
        }
        return None
    try:
        out = lg_exec("lg", "set", mode)
    except subprocess.CalledProcessError as e:
        log.exception("Setting mode failed")
        return str(e)
    except Exception as e:
        log.exception("Setting mode failed")
        return str(e)
    log.info("Output from 'lg set': %s" % out.decode())
    return None
