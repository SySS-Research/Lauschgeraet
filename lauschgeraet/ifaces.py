import os
import re
import subprocess
import netns
import logging
from lauschgeraet.lgiface import lg_exec, LG_NS
from lauschgeraet.args import LG_NS_MODE

log = logging.getLogger(__name__)


def cat(filename):
    with open(filename) as f:
        data = f.read()
    return data


def ls(path):
    return os.listdir(path)


def iptables_raw(table, chain=""):
    if ' ' in table or (chain and ' ' in chain):
        logging.error('Spaces not allowed table or chain name')
        return []
    if chain:
        chain = chain + " --line-numbers"
    cmd = 'iptables -t %s -L %s -v -n' % (table, chain)
    try:
        if LG_NS_MODE:
            with netns.NetNS(nsname=LG_NS):
                rules = subprocess.check_output(cmd.split())
        else:
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
    if len(rules) > 1:
        for m in p.finditer(rules[1]):
            keys.append((m.start(), m.group()))
        keys.append((keys[-1][0] + len(keys[-1][1]) + 2, "extension"))
        rules = rules[2:-1]
        result = []
        for r in rules:
            r = ({**{k[1]: r[k[0]:].split()[0] for k in keys[:-1]},
                  **{keys[-1][1]: r[keys[-1][0]:].strip()}})
            if "dpt:" in r["extension"]:
                r["destination"] = '%s:%s' % (
                        r["destination"],
                        r["extension"].split("dpt:")[1].split(" ")[0]
                )
            if "to:" in r["extension"]:
                r["extension"] = r["extension"].split("to:")[1]
            result.append(r)

        return result
    return []


def add_iptables_rule(proto, old_dest, old_port, new_dest, new_port):
    log.info('Adding mitm rule %s %s %s %s' % (
                proto, old_port, old_dest,
                new_dest))
    try:
        lg_exec(
            "lg-redirect add %s %s %s %s %s" % (
                proto,
                old_dest,
                old_port,
                new_dest,
                new_port,
            )
        )
    except Exception as e:
        log.error("%s: %s" % (str(e), e.stdout.decode()))
        return(str(e.stdout.decode()))
    return None


def replace_iptables_rule(n, proto, old_dest, old_port, new_dest, new_port):
    out = delete_iptables_rule(n)
    if out:
        return out
    out = add_iptables_rule(proto, old_dest, old_port, new_dest, new_port)
    if out:
        return out
    return ""


def delete_iptables_rule(n):
    log.info('Deleting mitm rule %s' % (n))
    try:
        lg_exec("lg-redirect del %d" % n)
    except Exception as e:
        log.error("%s: %s" % (e, e.stdout.decode()))
        return(str(e.stdout.decode()))
    return None


def get_ip_config():
    try:
        cmd = 'ip address show'
        if LG_NS_MODE:
            with netns.NetNS(nsname=LG_NS):
                result = subprocess.check_output(cmd.split())
        else:
            result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()


def get_ip_route():
    cmd = 'ip route show'
    try:
        if LG_NS_MODE:
            with netns.NetNS(nsname=LG_NS):
                result = subprocess.check_output(cmd.split())
        else:
            result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()


def get_ss():
    cmd = 'ss -ntulp'
    try:
        if LG_NS_MODE:
            with netns.NetNS(nsname=LG_NS):
                result = subprocess.check_output(cmd.split())
        else:
            result = subprocess.check_output(cmd.split())
    except Exception as e:
        logging.error(e)
        return ""
    return result.decode()
