"""This modules handles dependencies.

It should run under both python2 and python3.
"""


import subprocess
import os
import sys
import logging
log = logging.getLogger(__name__)


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dependencies_met():
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
        cmd = os.path.join(get_script_path(),
                           "lg-server",
                           "lg-setup.sh",
                           *args,
                           )
        log.info("Setting up the Lauschgerät by executing '%s'" % cmd)
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        log.error("Setup returned with code %d: %s, %s" % (e.returncode,
                                                           e.stdout.decode(),
                                                           e.stderr.decode(),
                                                           ))
        return False
    log.info("Setup successful: %s" % out.decode())
    return True
