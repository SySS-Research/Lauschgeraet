# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
import shutil
import netns
#  from lauschgeraet.args import LG_NS_MODE
from lauschgeraet.lgiface import LG_NS
from multiprocessing import Process, Queue
from queue import Empty

import logging

log = logging.getLogger(__name__)

MANDATORY_PARAMETERS = [
    "path",
    "argstring",
    "display_name",
    "parameters",
]

MANDATORY_PROPERTIES = [
    "description",
    "type",
]


def enqueue_output(out, queue):
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
    except KeyboardInterrupt:
        pass
    out.close()


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def list_installed_services():
    path = os.path.join(
        get_script_path(),
        "services",
    )
    result = os.listdir(path)
    result = [p.replace(".json", "") for p in result if p.endswith(".json")]
    return result


class MandatoryParameterNotFound(Exception):
    pass


class LGServiceParameter(object):
    def __init__(self, props):
        self._props = props
        for p in MANDATORY_PROPERTIES:
            if p not in self._props:
                raise MandatoryParameterNotFound(p)

    def __getitem__(self, key):
        return self._props[key]

    def update(self, value):
        self._props["value"] = value


class LGService(object):
    def __init__(self, jsonfile):
        filename = os.path.join(
            get_script_path(),
            "services",
            jsonfile + ".json",
        )
        self._dict = {}
        self._filename = filename
        with open(filename) as json_file:
            d = json.load(json_file)
        self._update_json(d)
        self.output = ""

    def _update_json(self, d):
        for p in MANDATORY_PARAMETERS:
            if p not in d:
                raise MandatoryParameterNotFound(p)
        for key, value in d["parameters"].items():
            d["parameters"][key] = LGServiceParameter(value)
        self._dict["parameters"] = d["parameters"]
        self._dict["properties"] = {
            "display_name": {
                "description": "Display Name",
                "type": "text",
                "help": "",
                "value": d["display_name"],
            },
            "path": {
                "description": "Path",
                "type": "text",
                "help": "System path to the executable",
                "value": d["path"],
            },
            "argstring": {
                "description": "Argument String",
                "type": "text",
                "help": "This string is passed to the executable as "
                        " arguments. Example: '-p %(port) -h %(host)'",
                "value": d["argstring"],
            },
            "python_reqs": {
                "description": "Python requirements",
                "type": "text",
                "help": "List of python3 packages which need to be "
                        "installed via pip3",
                "value": d["python_reqs"],
            },
            "system_reqs": {
                "description": "System requirements",
                "type": "text",
                "help": "List of packages which need to be installed via "
                        "apt-get",
                "value": d["system_reqs"],
            },
            "install_cmd": {
                "description": "Install Command",
                "type": "text",
                "help": "This command installs the actual executable ",
                "value": d["install_cmd"],
            },
            "update_cmd": {
                "description": "Update Command",
                "type": "text",
                "help": "This command updates the actual executable ",
                "value": d["update_cmd"],
            },
            "source": {
                "description": "Source",
                "type": "text",
                "help": "Where to get the executable",
                "value": d["source"],
            },
        }

    def start(self):
        # save thread
        # https://stackoverflow.com/questions/49492550/start-another-process-in-background-and-capture-output-in-python
        # https://stackoverflow.com/questions/16768290/understanding-popen-communicate
        # https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
        params = {key: value["value"] for key, value in
                  self._dict["parameters"].items()}
        args = self._dict["properties"]["argstring"]["value"] % params
        args = args.split()
        self.cmd = [self._dict["properties"]["path"]["value"]] + args
        log.info("Executing: %s" % ' '.join(self.cmd))
        with netns.NetNS(nsname=LG_NS):
            self._p = subprocess.Popen(['stdbuf', '-o0'] + self.cmd,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       bufsize=1,
                                       close_fds=True)
        self._q = Queue()
        self._tout = Process(target=enqueue_output, args=(self._p.stdout,
                                                          self._q))
        self._tout.daemon = True  # thread dies with the program
        self._tout.start()
        self._terr = Process(target=enqueue_output, args=(self._p.stderr,
                                                          self._q))
        self._terr.daemon = True  # thread dies with the program
        self._terr.start()

    def stop(self):
        # kill thread
        log.info("Killing: %s" % ' '.join(self.cmd))
        self._p.terminate()

    def pid(self):
        if self.running():
            return "%d" % self._p.pid
        return ""

    def running(self):
        try:
            return self._tout.is_alive()
        except AttributeError:
            return False

    def get_output(self):
        if not self.running():
            return "<not running>"
        while True:
            try:
                line = self._q.get_nowait()  # or q.get(timeout=.1)
                self.output += line.decode()
            except Empty:
                break
        return self.output

    def update_json(self, jsondata):
        d = json.loads(jsondata)
        self._update_json(d)

    def save_json(self):
        with open(self._filename, 'w') as outfile:
            json.dump(self._dict, outfile)

    def __getitem__(self, key):
        return self._dict[key]

    def is_installed(self):
        return shutil.which(self["properties"]["path"]["value"]) is not None

    def install_reqs(self):
        for r in self["properties"]["system_reqs"]["value"]:
            cmd = "apt-get install -yq".split() + [r]
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                log.exception("Exception while running command: %s" %
                              ' '.join(cmd))
                log.error(e.output.decode())
        for r in self["properties"]["python_reqs"]["value"]:
            cmd = "pip3 install --user".split() + [r]
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                log.exception("Exception while running command: %s" %
                              ' '.join(cmd))
                log.error(e.output.decode())

    def install(self):
        cmd = self["properties"]["install_cmd"]["value"].split()
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.exception("Exception while running command: %s" %
                          ' '.join(cmd))
            log.error(e.output.decode())

    def update(self):
        cmd = self["properties"]["update_cmd"]["value"].split()
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.exception("Exception while running command: %s" %
                          ' '.join(cmd))
            log.error(e.output.decode())

    def update_params(self, d):
        """Update arguments based on the values in the dictionary d"""
        for k, v in d.items():
            if k in self["parameters"]:
                self["parameters"][k].update(v)


SERVICES = [LGService(s) for s in list_installed_services()]
