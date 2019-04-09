# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import logging
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


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dependencies_met():
    if TEST:
        return True
    for f in [
        "lg",
        "lg-allif",
        "lg-arp.py",
        "lg-arptab",
        "lg-brif",
        "lg-config.sh",
        "lg-getgw",
        "lg-nat",
        "lg-redirect",
        "lg-wifi",
    ]:
        if not os.path.isfile(os.path.join(os.sep, 'usr', 'sbin', f)):
            return False
    # check for python3
    if sys.version_info < (3, 0):
        return False
    # python modules are checked implicitily via except ImportError
    return True


def lg_setup(*args):
    try:
        cmd = [
            os.path.join(
                get_script_path(),
                "lg-server",
                "lg-setup.sh"
            )
        ] + [x[0] for x in args]
        log.info("Setting up the Lauschgerät by executing '%s'" % cmd)
        o = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
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
    output = subprocess.check_output(['lg', 'status'],
                                     stderr=subprocess.STDOUT)
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
        out = subprocess.check_output(
            ["lg", "set", mode],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        log.error("Setting mode failed: %s" % e.stdout.decode())
        return e.stdout.decode()
    except Exception as e:
        log.error("Setting mode failed: %s" % e)
        return str(e)
    log.info("Output from 'lg set': %s" % out.decode())
    return None
