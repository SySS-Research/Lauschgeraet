# -*- coding: utf-8 -*-

import subprocess
import os
import logging
log = logging.getLogger(__name__)

TEST = os.path.exists('testing')


def get_lg_status():
    if TEST:
        return {
            "lgstate": {
                "enabled": True,
                "mode": "passive",
            }
        }
    cmd = 'lg status'
    output = subprocess.check_output(cmd.split(), shell=True)
    # the cmd returns one of the following:
    # * passive
    # * active
    # * wifi
    # * disabled
    return {
        "lgstate": {
            "enabled": not output == b'disabled',
            "mode": output.decode(),
        }
    }


def activate_lg():
    log.info("Activate Lauschgerät")


def set_lg_mode(mode):
    log.info("Setting Lauschgerät to '%s'" % mode)
    try:
        subprocess.check_output(["lg", "set", mode], shell=True)
    except subprocess.CalledProcessError as e:
        log.error("Setting mode failed: %s" % e.stdout.decode())
        return e.stdout.decode()
    return "OK"
