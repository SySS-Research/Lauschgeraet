#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from lauschgeraet.dependencies import dependencies_met


logging.basicConfig(
    filename='/var/log/lauschgeraet.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    log.info("Starting lauschgeraet.py")
    if dependencies_met():
        import lauschgeraet.flask as lf
        lf.main()
    else:
        log.warning("Dependencies not met, launching basic web server")
        import lauschgeraet.initial_webserver as iws
        iws.run('0.0.0.0', 1337)
