import os
import re
import subprocess
import logging


def cat(filename):
    with open(filename) as f:
        data = f.read()
    return data


def ls(path):
    return os.listdir(path)


def list_devices():
    return ls('/sys/class/net/')


def iptables_raw(table, chain):
    if ' ' in table or ' ' in chain:
        logging.error('Spaces not allowed table or chain name')
        return []
    cmd = 'iptables -t %s -L %s -v -n --line-numbers' % (table, chain)
    try:
        rules = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return []
    return rules


def list_iptables(table, chain):
    rules = iptables_raw(table, chain)
    rules = rules.decode().split('\n')
    keys = []
    p = re.compile(r'\b\w+\b')
    for m in p.finditer(rules[1]):
        keys.append((m.start(), m.group()))
    rules = rules[2:-1]
    result = []
    for r in rules:
        result.append({k[1]: r[k[0]:].split()[0] for k in keys})

    return result


def get_ip_config(n):
    devs = list_devices()
    cmd = 'ip address show %s' % devs[n]
    try:
        result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()


def get_ip_route():
    cmd = 'ip route show'
    try:
        result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()
