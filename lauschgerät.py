#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lauschgeraet.dependencies import dependencies_met

if __name__ == "__main__":
    if dependencies_met():
        import lauschgeraet.flask
        lauschgeraet.flask.main()
    else:
        import lauschgeraet.inital_webserver as iws
        iws.run('0.0.0.0', 1337)
