#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from lauschgeraet.dependencies import dependencies_met


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/lauschgeraet.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
fh.setFormatter(formatter)
log.addHandler(fh)


if __name__ == "__main__":
    log.info("Starting lauschgeraet.py")
    if dependencies_met():
        import lauschgeraet.flask as lf
        lf.main()
    else:
        log.warning("Dependencies not met, launching basic web server")
        import lauschgeraet.initial_webserver as iws
        iws.run('0.0.0.0', 1337)
