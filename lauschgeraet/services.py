# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
import netns
import logging
from lauschgeraet.args import LG_NS_MODE

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


def get_services():
    return [LGService(s) for s in list_installed_services()]


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
        }

    def start(self):
        pass

    def stop(self):
        pass

    def get_output(self):
        pass

    def update_json(self, jsondata):
        d = json.loads(jsondata)
        self._update_json(d)

    def save_json(self):
        with open(self._filename, 'w') as outfile:
            json.dump(self._dict, outfile)

    def __getitem__(self, key):
        return self._dict[key]
