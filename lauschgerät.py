#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from lauschgeraet.lgiface import init_ns, teardown_ns


logging.basicConfig(
    handlers=[logging.FileHandler('/var/log/lauschgeraet.log', 'a', 'utf-8')],
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


if __name__ == "__main__":
    log.info("Starting lauschgeraet.py")
    try:
        import lauschgeraet.flask as lf
        try:
            init_ns()
            lf.main()
        finally:
            teardown_ns()
    except ImportError:
        log.critical("Dependencies not met, consult the Readme")
