"""This modules handles dependencies.

It should run under both python2 and python3.
"""


from subprocess import check_output

import os
import sys


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


def dependency_check():
    return "TODO_DEP_CHECK"


def install_dependencies():
    out = check_output(os.path.join(get_script_path(),
                                    "bin",
                                    "install_deps.sh"))
    return 'SUCCESS' in out
