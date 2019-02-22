from subprocess import check_output

import os
import sys


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def dependencies_met():
    return True


def install_dependencies():
    out = check_output(os.path.join(get_script_path,
                                    "bin",
                                    "install_deps.sh"))
    return 'SUCCESS' in out


def dependency_check():
    return "TODO_DEP_CHECK"
