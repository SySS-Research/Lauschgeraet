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
                "active": True,
                "wifi": False,
                "status": "active",
            }
        }
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
    try:
        subprocess.check_output(
            ["lg", "set", mode],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        log.error("Setting mode failed: %s" % e.stdout.decode())
        return e.stdout.decode()
    except Exception as e:
        log.error("Setting mode failed: %s" % e)
        return str(e)
    return None
