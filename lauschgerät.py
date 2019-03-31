#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from lauschgeraet.dependencies import dependencies_met


logging.basicConfig(
    handlers=[logging.FileHandler('/var/log/lauschgeraet.log', 'w', 'utf-8')],
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    log.info("Starting lauschgeraet.py")
    DEPS_MET = dependencies_met()
    if DEPS_MET:
        try:
            import lauschgeraet.flask as lf
            lf.main()
        except ImportError as e:
            # Not all dependencies were met after all
            DEPS_MET = False
            log.warning("Missing module: %s" % str(e))
    if not DEPS_MET:
        log.warning("Dependencies not met, launching basic web server")
        import lauschgeraet.initial_webserver as iws
        iws.run('0.0.0.0', 1337)
