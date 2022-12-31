#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paste subapp resoureces"""

import string

from .. import config


def generate_id() -> str:
    return "".join(config.RANDOM.choices(string.ascii_letters + string.digits, k=10))
