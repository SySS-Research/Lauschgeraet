# -*- coding: utf-8 -*-

from lauschgeraet.args import args
import subprocess
import os
import sys
import logging
import netns
log = logging.getLogger(__name__)

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
SW_IFACE = args.SW_IFACE
CL_IFACE = args.CL_IFACE

ns_setup = [
    # create a network namespace
    'ip netns add ' + LG_NS,

    # Assign the "inside" interface to the network namespace
    'ip link set netns %s %s' % (LG_NS, SW_IFACE),
    'ip link set netns %s %s' % (LG_NS, CL_IFACE),
]

ns_teardown = [
    'ip netns del %s' % LG_NS,
]


def run_steps(steps, ignore_errors=False):
    for step in steps:
        try:
            print('+ {}'.format(step))
            subprocess.check_call(step, shell=True)
        except subprocess.CalledProcessError:
            if ignore_errors:
                pass
            else:
                raise


def init_ns():
    run_steps(ns_setup)


def teardown_ns():
    run_steps(ns_teardown)


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dependencies_met():
    if TEST:
        return True
    # TODO check for actual deps
    # check for python3
    if sys.version_info < (3, 0):
        return False
    # python modules are checked implicitily via except ImportError
    return True


def lg_exec(*args):
    cmd = [
        os.path.join(
            get_script_path(),
            "lg-server",
        )
    ] + [x[0] for x in args]
    with netns.NetNS(nsname=LG_NS):
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return output


def lg_setup(*args):
    try:
        log.info("Setting up the Lauschgerät")
        o = lg_exec("lg-setup.sh",)
    except subprocess.CalledProcessError as e:
        if sys.version_info > (3, 0):
            strings = (e.returncode, e.stdout.decode())
        else:
            strings = (e.returncode, e.output)
        log.error("Setup returned with code %d: %s" % strings)
        return False
    if sys.version_info >= (3, 0):
        log.info("Setup successful: %s" % o.decode())
    else:
        log.info("Setup successful: %s" % o)
    return True


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
        log.error("Setting mode failed: %s" % e.stdout.decode())
        return e.stdout.decode()
    except Exception as e:
        log.error("Setting mode failed: %s" % e)
        return str(e)
    log.info("Output from 'lg set': %s" % out.decode())
    return None
