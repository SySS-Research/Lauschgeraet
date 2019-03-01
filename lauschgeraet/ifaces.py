import os
import re
import subprocess
import logging

log = logging.getLogger(__name__)


def cat(filename):
    with open(filename) as f:
        data = f.read()
    return data


def ls(path):
    return os.listdir(path)


def list_devices():
    return ls('/sys/class/net/')


def iptables_raw(table, chain=""):
    if ' ' in table or (chain and ' ' in chain):
        logging.error('Spaces not allowed table or chain name')
        return []
    if chain:
        chain = chain + " --line-numbers"
    cmd = 'iptables -t %s -L %s -v -n' % (table, chain)
    try:
        rules = subprocess.check_output(cmd.split())
    except Exception as e:
        log.error(e)
        return b""
    return rules


def list_iptables(table, chain):
    rules = iptables_raw(table, chain)
    rules = rules.decode().split('\n')
    keys = []
    p = re.compile(r'\b\w+\b')
    for m in p.finditer(rules[1]):
        keys.append((m.start(), m.group()))
    keys.append((keys[-1][0] + len(keys[-1][1]) + 2, "extension"))
    rules = rules[2:-1]
    result = []
    for r in rules:
        result.append({**{k[1]: r[k[0]:].split()[0] for k in keys[:-1]},
                       **{keys[-1][1]: r[keys[-1][0]:].strip()}})

    return result


def add_iptables_rule(proto, port, old_dest, new_dest):
    # TODO replace with lg shell script
    log.info('Adding iptables rule %s %s %s %s' % (proto, port, old_dest,
                                                   new_dest))
    chain = 'PREROUTING'
    try:
        result = subprocess.check_output('iptables -t nat -A'.split() +
                                         [chain, '-p', proto, '-d', old_dest,
                                          '--dport', port, '-j', 'DNAT',
                                          '--to-destination', new_dest],
                                         stderr=subprocess.STDOUT,)
    except Exception as e:
        log.error(e)
    return result


def replace_iptables_rule(n, proto, port, old_dest, new_dest):
    # TODO replace with lg shell script
    log.info('Replacing iptables rule %s %s %s %s %s' % (n, proto, port,
                                                         old_dest, new_dest))
    chain = 'PREROUTING'
    try:
        result = subprocess.check_output('iptables -t nat -R'.split() +
                                         [chain, n, '-p', proto, '-d',
                                          old_dest, '-j', 'DNAT',
                                          '--to-destination', new_dest],
                                         stderr=subprocess.STDOUT,)
    except Exception as e:
        logging.error(e)
    return result


def delete_iptables_rule(n):
    # TODO replace with lg shell script
    log.info('Deleting iptables rule %s' % (n))
    chain = 'PREROUTING'
    try:
        result = subprocess.check_output('iptables -t nat -D'.split() +
                                         [chain, n],
                                         stderr=subprocess.STDOUT,)
    except Exception as e:
        logging.error(e)
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


def get_ss():
    cmd = 'ss -ntulp'
    try:
        result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()
