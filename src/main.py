#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""homeserver"""

import sys
from warnings import filterwarnings as filter_warnings

from homeserver import config, create_homeserver


def main() -> int:
    """Entry/main function"""

    create_homeserver().run(config.HOST, config.PORT)

    return 0


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    sys.exit(main())
