import subprocess


def get_lg_status():
    cmd = 'lg status'
    output = subprocess.check_output(cmd.split())
    try:
        return output.decode()
    except KeyError:
        return None
