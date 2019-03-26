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
                "enabled": False,
                "mode": "deactivated",
            }
        }
    cmd = 'lg status'
    output = subprocess.check_output(cmd.split())
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
